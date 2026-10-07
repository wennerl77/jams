# ⚡ JAMS — Judge Assessment & Metrics Suite

> **Plataforma de Teste de Carga, Observabilidade em Tempo Real e Telemetria para Helium (MicroHelium)**

O **JAMS** (*Judge Assessment & Metrics Suite*) é uma suíte de testes de carga, observabilidade em tempo real e telemetria de sistema dedicada exclusivamente à plataforma de maratona de programação **Helium** (**MicroHelium**).

O objetivo do JAMS é avaliar e perfilar a resiliência, latência de julgamento e consumo de recursos sob condições de alto tráfego e submissões concorrentes. A stack do Helium opera sob **Docker Compose** nativo com isolamento rigoroso via cgroups no host Linux, distribuindo cotas previsíveis entre os microsserviços da aplicação (Webserver Nginx, Aplicação Laravel PHP-FPM, Cache/Filas Redis, Banco de Dados MySQL e Worker de Julgamento Autojudge).

---

## 📐 Topologia da Arquitetura & Infraestrutura

A stack do Helium opera sob **Docker Compose** (`docker-compose.helium.yml` / `docker-compose.yml`) com cgroups v2 no host Linux. O ecossistema completo opera com uma cota consolidada de **2.00 vCPUs**, **2048 MB RAM**, `blkio_config: { weight: 500 }`, 0 VRAM/GPU e sem swap:

```
                  +-------------------------------------------------------------+
                  |                         HOST LOCAL                          |
                  |     JAMS Control Master & Loadgen                           |
                  |     (Locust + Live Dashboard + Telemetria cgroups)          |
                  +------------------------------+------------------------------+
                                                 |
                                                 | HTTP (127.0.0.10:8000 / :8443)
                                                 v
                  +-------------------------------------------------------------+
                  |                    STACK HELIUM (Docker)                    |
                  |         IP Local: 127.0.0.10 | Total: 2.0 CPU / 2048 MB     |
                  |         Arquivo: docker-compose.helium.yml                  |
                  |                                                             |
                  |  [Camada Web]                                               |
                  |  - helium-webserver (Nginx Alpine): 0.20 CPU / 128 MB RAM   |
                  |    Portas: 127.0.0.10:8000, :8010, :8443                    |
                  |                                                             |
                  |  [Camada de Aplicação]                                      |
                  |  - helium-app (PHP 8.3-FPM + Laravel): 0.25 CPU / 320 MB    |
                  |    Comunicação interna FastCGI (porta 9000)                 |
                  |                                                             |
                  |  [Camada de Cache & Filas]                                  |
                  |  - helium-redis (Redis 7 Alpine): 0.05 CPU / 64 MB RAM      |
                  |    Portas: 127.0.0.10:6379, :6380 (Queue & Session Cache)   |
                  |                                                             |
                  |  [Camada de Julgamento Automático]                          |
                  |  - helium-autojudge (Worker SYS_PTRACE): 1.00 CPU / 1024 MB |
                  |    Execução com safeexec + compiladores g++/gcc/python      |
                  |                                                             |
                  |  [Camada de Dados]                                          |
                  |  - helium-db (MySQL 8.0): 0.50 CPU / 512 MB RAM             |
                  |    Portas: 127.0.0.10:3306, :3307                           |
                  |                                                             |
                  |  Rede: helium-net (172.28.2.0/24, MTU 1500)                 |
                  |  Telemetria: cgroups v2 / docker stats a cada 1s            |
                  +-------------------------------------------------------------+
```

---

## ⚙️ Cota de Hardware e Distribuição de Recursos

A distribuição de recursos entre os 5 containers da stack Helium garante estabilidade e isolamento de processos:

| Container | Camada / Função | Cota CPU | Cota RAM | Swap | Disk I/O Weight | Portas Host |
|---|---|---|---|---|---|---|
| `helium-webserver` | Servidor Web (Nginx Alpine) | **0.20 vCPU** | **128 MB** | Desativado (`mem = swap`) | 500 | `127.0.0.10:8000`, `:8010`, `:8443` |
| `helium-app` | Aplicação Core (PHP 8.3-FPM / Laravel) | **0.25 vCPU** | **320 MB** | Desativado (`mem = swap`) | 500 | Interna FastCGI `:9000` |
| `helium-redis` | Cache & Filas de Mensagens (Redis 7) | **0.05 vCPU** | **64 MB** | Desativado (`mem = swap`) | 500 | `127.0.0.10:6379`, `:6380` |
| `helium-autojudge` | Motor de Julgamento (`SYS_PTRACE`, safeexec) | **1.00 vCPU** | **1024 MB** | Desativado (`mem = swap`) | 500 | Interna (`helium-net`) |
| `helium-db` | Banco de Dados Relacional (MySQL 8.0) | **0.50 vCPU** | **512 MB** | Desativado (`mem = swap`) | 500 | `127.0.0.10:3306`, `:3307` |
| **TOTAL CONSOLIDADO** | **5 microsserviços integrados** | **2.00 vCPUs** | **2048 MB** | **0 MB** | **500** | — |

---

## 🛠️ Pré-requisitos do Sistema

- **Linux (Ubuntu / Debian / Arch / Fedora)**
- **Docker & Docker Compose v2+**
- **Python 3.11+**
- **GNU Make**

---

## 🚀 Guia de Execução Rápida

### 🟢 Início Rápido

```bash
# 1. Instalar dependências Python no ambiente virtual (loadgen/venv)
make setup

# 2. Compilar imagens e subir os containers do Helium
make build
make up

# 3. Restaurar e popular o banco de dados do Helium em estado limpo
make reset-db

# 4. Validar submissão de teste na plataforma Helium
make test-submission TARGET=helium FILE=ac_sum.cpp LANG=cpp

# 5. Iniciar o Live Dashboard Web em Tempo Real (compila e sobe os containers automaticamente!)
make dashboard
```
Acesse no navegador: **`http://localhost:8501`**

---

## ⚙️ Matriz de Comandos Automáticos (`Makefile`)

### Comandos Globais (Unificados)
| Comando | Descrição |
|---|---|
| `make setup` | Cria o ambiente virtual `loadgen/venv` e instala todas as dependências Python. |
| `make build` | Compila as imagens Docker da stack Helium (`helium-build`). |
| `make up` | Sobe todos os containers Docker da stack Helium (2 vCPU / 2GB RAM total). |
| `make down` | Para e remove todos os containers Docker da stack Helium. |
| `make ps` | Exibe o status e consumo dos containers da stack Helium. |
| `make logs` | Exibe os logs unificados de todos os containers da stack Helium. |
| `make reset-db` | Restaura e popula o banco de dados do Helium (MySQL) em estado limpo. |
| `make dashboard` | Constrói, sobe a stack Helium e inicia a interface Streamlit em `http://localhost:8501`. |
| `make test-submission` | Envia submissão de teste individual (`TARGET=helium FILE=ac_sum.cpp LANG=cpp`). |
| `make clean` | Limpa logs, filas e arquivos transitórios de resultados. |

### Comandos Dedicados da Stack Helium
| Comando | Descrição |
|---|---|
| `make helium-build` | Compila as imagens Docker da stack Helium (`docker-compose.helium.yml`). |
| `make helium-up` | Sobe apenas os containers da stack Helium (2 vCPU / 2048 MB RAM). |
| `make helium-down` | Para e remove apenas os containers da stack Helium. |
| `make helium-ps` | Exibe o status dos containers da stack Helium. |
| `make helium-logs` | Exibe os logs dos containers da stack Helium. |
| `make reset-db-helium` | Restaura e popula o banco de dados do Helium (MySQL). |
| `make load-helium` | Executa o gerador de carga Locust contra o Helium (`http://127.0.0.10:8000`). |
| `make collect-helium` | Inicia coleta de telemetria de containers do Helium (`SCENARIO=burst INTERVAL=1s`). |

---

## 🎯 Cenários de Teste de Carga Suportados (`SCENARIO`)

Altere o perfil de carga passando a variável `SCENARIO`:

- `burst`: Pico instantâneo de submissões simultâneas (ex: abertura de prova).
- `baseline`: Carga constante de 1 usuário por 2 minutos (latência mínima de referência).
- `steady`: Carga contínua estável por 25 minutos.
- `ramp`: Degraus crescentes (ex: 10 → 25 → 50 → 100 usuários).
- `endurance`: Teste de longa duração para detectar degradação e vazamentos de memória.

Exemplo:
```bash
make load-helium SCENARIO=burst USERS=20
```

---

## 📁 Estrutura de Diretórios do Projeto

```
jams/
├── docker-compose.helium.yml  # Especificação da stack Helium (limits, services & networks)
├── docker-compose.yml         # Especificação unificada Compose
├── Makefile                   # Automação de comandos dedicados e globais
├── README.md                  # Visão geral e guia de uso do sistema
├── AGENTS.md                  # Especificação técnica e manifesto de engenharia
├── docs/
│   └── MULTI_SERVICE_OBSERVABILITY.md # Guia de topologia e catálogo de observabilidade
├── analysis/
│   ├── live_dashboard.py      # Live Dashboard Web em Streamlit + Plotly
│   └── requirements.txt       # Dependências da interface de observabilidade
├── loadgen/
│   ├── locustfile.py          # Script de carga Locust (HeliumUser via REST API)
│   ├── submitter.py           # Submissor CLI para validação e testes individuais
│   ├── scenarios/             # Perfis de teste de carga (burst, ramp, steady, etc.)
│   └── submissions/           # Códigos de teste (AC, WA, TLE, CE em C++, Python, Java)
├── monitoring/
│   ├── docker-collect.py      # Coletor de métricas de cgroups do Docker em tempo real
│   ├── sar-collect.sh         # Script de acionamento de telemetria
│   └── queue_manager.py       # Gerenciador de fila e telemetria de vereditos
└── provisioning/
    ├── reset_databases.sh     # Script de restauração limpa do banco de dados (--helium)
    └── helium/                # Seeds do MySQL (Contest, Problems, Users, Testcases)
```

---

## 📜 Licença

Este projeto é desenvolvido para fins acadêmicos, pesquisa e testes de carga em sistemas de julgamento automático de maratona de programação.
