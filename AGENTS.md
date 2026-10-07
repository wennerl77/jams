# Stack Tecnológica & Especificação de Teste de Carga e Observabilidade — Helium (MicroHelium) Docker Edition

> **Instruções para Agentes e Desenvolvedores**:  
> Este documento serve como referência técnica primária para qualquer agente ou engenheiro que opere neste repositório. O objetivo do projeto é testar, avaliar e perfilar a performance, latência de julgamento, utilização de recursos e resiliência da plataforma **Helium (MicroHelium)** sob condições controladas, reprodutíveis e com limites estritos de recursos no Docker Compose.

---

## Visão Geral

O ambiente de testes opera exclusivamente sob **Docker Compose** nativo (`docker-compose.helium.yml` / `docker-compose.yml`) com isolamento de cgroups v2 no host Linux. A stack do Helium é composta por 5 microsserviços integrados sob uma cota consolidada de hardware de **2.0 vCPUs**, **2048 MB RAM**, `blkio_config: { weight: 500 }`, ausência de swap e isolamento de rede:

```
                  +-------------------------------------------------------------+
                  |                         HOST LINUX                          |
                  |  Locust Runner (Python 3.11+) + Docker CGroup Telemetry     |
                  +------------------------------+------------------------------+
                                                 |
                                                 | HTTP (127.0.0.10:8000 / :8443)
                                                 v
+-------------------------------------------------------------------------------+
|                             STACK HELIUM (Docker)                             |
|             IP: 127.0.0.10 | Cota Total: 2.0 CPU / 2048 MB RAM                |
|             Arquivo: docker-compose.helium.yml / docker-compose.yml           |
|                                                                               |
| - helium-webserver (Nginx Alpine):                                            |
|   0.20 CPU / 128 MB RAM (Portas: 127.0.0.10:8000, :8010, :8443)              |
|                                                                               |
| - helium-app (PHP 8.3-FPM, Laravel):                                          |
|   0.25 CPU / 320 MB RAM (FastCGI interna porta 9000)                          |
|                                                                               |
| - helium-redis (Redis 7 Alpine):                                              |
|   0.05 CPU / 64 MB RAM (Portas: 127.0.0.10:6379, :6380)                       |
|                                                                               |
| - helium-autojudge (Worker SYS_PTRACE SafeExec):                              |
|   1.00 CPU / 1024 MB RAM (Julgamento assíncrono g++, gcc, safeexec)           |
|                                                                               |
| - helium-db (MySQL 8.0):                                                      |
|   0.50 CPU / 512 MB RAM (Portas: 127.0.0.10:3306, :3307)                      |
|                                                                               |
| Redes: helium-net (172.28.2.0/24, MTU 1500)                                   |
| Telemetria: cgroups v2 / docker stats (amostragem a cada 1s)                  |
+-------------------------------------------------------------------------------+
```

---

## 1. Distribuição e Limites de Recursos

A cota consolidada de 2.0 vCPU e 2048 MB RAM é distribuída entre os componentes da stack:

| Componente / Container | Função / Serviço | Cota CPU | Cota RAM | Swap | Disk I/O Weight |
|---|---|---|---|---|---|
| `helium-autojudge` | Motor de Julgamento (safeexec + compilers) | **1.00 vCPU** | **1024 MB** | Desativado (`memswap = mem`) | 500 |
| `helium-db` | Banco de Dados Relacional (MySQL 8.0) | **0.50 vCPU** | **512 MB** | Desativado (`memswap = mem`) | 500 |
| `helium-app` | Aplicação Core (PHP 8.3-FPM / Laravel) | **0.25 vCPU** | **320 MB** | Desativado (`memswap = mem`) | 500 |
| `helium-webserver` | Servidor Web Reverso (Nginx Alpine) | **0.20 vCPU** | **128 MB** | Desativado (`memswap = mem`) | 500 |
| `helium-redis` | Cache de Aplicação e Filas de Tarefas (Redis 7) | **0.05 vCPU** | **64 MB** | Desativado (`memswap = mem`) | 500 |
| **TOTAL CONSOLIDADO** | **5 containers integrados** | **2.00 vCPUs** | **2048 MB** | **0 MB** | **500** |

> **GPU / VRAM**: Aceleração de vídeo e GPU estritamente desabilitadas (`device_requests: []`).  
> **Isolamento de Rede**: `helium-net` (`172.28.2.0/24`) opera em bridge Docker isolada com MTU 1500.

---

## 2. Endereçamento e Acesso

| Serviço | IP / Host Bind | Porta Interna | Porta Externa Host | Protocolo / Descrição |
|---|---|---|---|---|
| **Helium Web** | `127.0.0.10` | `80` | `127.0.0.10:8000` (e `8010`) | HTTP (Nginx / PHP-FPM) |
| **Helium SSL** | `127.0.0.10` | `443` | `8443` | HTTPS (Nginx) |
| **Helium DB** | `127.0.0.10` | `3306` | `127.0.0.10:3306` (e `3307`) | MySQL 8.0 (`microhelium` / `secret`) |
| **Helium Redis**| `127.0.0.10` | `6379` | `127.0.0.10:6379` (e `6380`) | Redis 7 (Cache e Queues) |
| **Dashboard** | `localhost` | `8501` | `http://localhost:8501` | Streamlit + Plotly Live Telemetry |

---

## 3. Especificação do Alvo Helium (MicroHelium)

- **Autenticação**: API REST JSON em `POST /api/login` retornando token Sanctum (`Bearer <token>`).
- **Submissão**: `POST /api/runs` via `multipart/form-data` (`contest_id`, `problem_id`, `language_id`, `source_file`) retornando HTTP 201 com o objeto Run.
- **Julgamento**: `helium-autojudge` executando `php artisan queue:work --sleep=1 --tries=3` em container privilegiado com `cap_add: [SYS_PTRACE]`, compilando fontes (`g++`, `gcc`, etc.) e executando casos de teste via `safeexec`.
- **Polling de Veredito**: Polling REST em `GET /api/runs/{id}` com extração direta de `status`, `answer_id` e `auto_judge_result`.

---

## 4. Telemetria e Coleta de Métricas

O script `monitoring/docker-collect.py` coleta métricas a cada 1 segundo diretamente dos cgroups do Docker via `docker stats --no-stream` para todos os containers do Helium:
- **CPU%**: Percentual de uso de CPU normalizado por container e consolidado.
- **RAM Utilizada (MB)**: Consumo real de memória dos containers da stack.
- **CSV Output**: `results/helium/<scenario>/sar_metrics.csv` com esquema padronizado compatível com o dashboard e análise em pandas.

O script `monitoring/sar-collect.sh` executa `docker-collect.py` de forma síncrona ou em background durante os testes de carga:
```bash
./monitoring/sar-collect.sh helium burst 1
```

---

## 5. Como Executar os Testes de Carga

### Fluxo com Makefile

```bash
# 1. Instalar dependências Python no ambiente virtual (loadgen/venv)
make setup

# 2. Compilar imagens e subir os containers do Helium
make build
make up

# 3. Resetar e popular o banco de dados do Helium em estado limpo
make reset-db

# 4. Validar submissão individual na API do Helium
make test-submission TARGET=helium FILE=ac_sum.cpp LANG=cpp

# 5. Iniciar o Live Dashboard Web em http://localhost:8501 (compila e sobe automaticamente!)
make dashboard

# 6. Executar teste de carga Locust contra o Helium
make load-helium SCENARIO=burst USERS=10
```

### Comandos de Gestão da Stack Helium

```bash
make helium-build       # Compila imagens Docker do Helium
make helium-up          # Sobe containers da stack Helium
make helium-down        # Para e remove containers do Helium
make helium-ps          # Exibe status dos containers
make helium-logs        # Exibe logs dos containers do Helium
make reset-db-helium    # Restaura e popula banco MySQL do Helium
make collect-helium     # Inicia telemetria dos containers do Helium
```

---

## 6. Diretrizes e Regras Operacionais para Agentes de IA

1. **Foco Exclusivo no Helium**: O repositório e seus módulos de carga, automação e observabilidade são dedicados exclusivamente à stack Helium (MicroHelium). Não reintroduza referências ou fluxos de execução legados.
2. **Cota e Alocação de Recursos Estrita**: Respeite a cota consolidada de 2.0 vCPUs e 2048 MB RAM distribuída entre os 5 containers do Helium (`helium-webserver`, `helium-app`, `helium-redis`, `helium-autojudge`, `helium-db`).
3. **Ambiente Limpo Pré-Teste**: Execute `make reset-db` (ou `make reset-db-helium`) antes de rodar qualquer bateria de medição para evitar resíduos de runs anteriores nas filas do Redis e tabelas do MySQL.
4. **Isolamento de Recursos**: O Locust, a telemetria e o Dashboard executam no host fora dos containers do Helium para não poluir o consumo de CPU/RAM da instância testada.
5. **Massa de Testes Padronizada**: Mantenha os códigos-fonte em `loadgen/submissions/` para validação fiel dos tempos de compilação e vereditos.
6. **Exclusividade Docker Compose**: É estritamente proibido utilizar máquinas virtuais (Vagrant/VirtualBox). Toda execução, orquestração, teste de carga e telemetria ocorre exclusivamente via containers Docker Compose (`docker-compose.helium.yml` / `docker-compose.yml`) e cgroups nativos do host Linux.
