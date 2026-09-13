# ⚡ JAMS — Judge Assessment & Metrics Suite

> **Plataforma de Benchmark Comparativo e Observabilidade Multi-Serviço para Juízes Automáticos (BOCA vs Helium)**

O **JAMS** (*Judge Assessment & Metrics Suite*) é uma suíte de testes de carga, observabilidade em tempo real e telemetria de SO projetada para avaliar e comparar a performance, latência de julgamento e utilização de recursos entre diferentes plataformas de maratona de programação (**BOCA** e **Helium**) sob condições de hardware rigorosamente idênticas.

---

## 📐 Topologia da Arquitetura & Infraestrutura

O ambiente opera em duas máquinas virtuais gerenciadas pelo **Vagrant** (VirtualBox) no host local, cada uma provida com **2 vCPU / 2048 MB RAM** rodando **Ubuntu 22.04 LTS**:

```
                                +-------------------------------------------+
                                |               HOST LOCAL                  |
                                |     JAMS Control Master & Loadgen         |
                                |     (Locust + Live Dashboard + sar)       |
                                +--------------------+----------------------+
                                                     |
                     +-------------------------------+-------------------------------+
                     |                                                               |
                     v (HTTP :8000 / SSH)                                            v (HTTP :8000 / SSH)
  +--------------------------------------------------+   +--------------------------------------------------+
  |               VM 1: BOCA (`boca`)                |   |              VM 2: Helium (`helium`)             |
  |             IP Privado: 192.168.56.11            |   |            IP Privado: 192.168.56.10             |
  |                                                  |   |                                                  |
  | - Docker Containers:                             |   | - Docker Containers:                             |
  |   - `boca-web` (Apache + PHP) :8000->:80         |   |   - `webserver` (Nginx Alpine) :8000->:80, :8443 |
  |   - `boca-jail` (AutoJudge Jail chroot)          |   |   - `app` (PHP 8.3-FPM + Laravel 12/13)          |
  |   - `boca-db` (PostgreSQL 14) :5432              |   |   - `db` (MySQL 8.0) :3306                       |
  | - Daemons do SO:                                 |   |   - `redis` (Redis 7 Cache & Queue) :6379        |
  |   - `sysstat` / `sar` daemon (Amostragem: 1s)    |   |   - `autojudge` (Worker SYS_PTRACE)              |
  |                                                  |   | - Daemons do SO:                                 |
  |                                                  |   |   - `sysstat` / `sar` daemon (Amostragem: 1s)    |
  +--------------------------------------------------+   +--------------------------------------------------+
```

---

## 🛠️ Pré-requisitos do Sistema

Antes de iniciar, certifique-se de possuir instalado na máquina host:
- **Python 3.11+**
- **Vagrant** & **VirtualBox**
- **GNU Make**
- **Git**

---

## 🚀 Guia de Início Rápido (Quickstart)

### 1. Clonar o Repositório e Instalar Dependências

```bash
git clone git@github.com:wennerl77/jams.git
cd jams

# Instala todas as dependências em um ambiente virtual isolado (venv/)
make setup
```

### 2. Subir as VMs Vagrant e Preparar os Bancos de Dados

```bash
# Sobe os containers Docker dentro das VMs e restaura o banco em estado limpo de paridade
make reset-db SYSTEMS=true
```

### 3. Iniciar o Live Dashboard Web (Tempo Real)

```bash
make dashboard
```
Acesse no navegador: **`http://localhost:8501`**

---

## 📊 Como Rodar os Benchmarks de Carga & Telemetria

O fluxo de testes deve ser executado com o **Live Dashboard** aberto para acompanhamento visual das métricas.

### Execução no BOCA
```bash
# Terminal 1: Iniciar coleta de telemetria de CPU/RAM (VM BOCA)
make collect-boca SCENARIO=burst INTERVAL=1

# Terminal 2: Disparar carga de submissões concorrentes (Locust)
make load-boca SCENARIO=burst USERS=10
```

### Execução no Helium
```bash
# Terminal 1: Iniciar coleta de telemetria de CPU/RAM (VM Helium)
make collect-helium SCENARIO=burst INTERVAL=1

# Terminal 2: Disparar carga de submissões concorrentes (Locust)
make load-helium SCENARIO=burst USERS=10
```

---

## ⚙️ Matriz de Comandos Automáticos (`Makefile`)

| Comando | Descrição |
|---|---|
| `make setup` | Cria o ambiente virtual `venv/` e instala todas as dependências Python. |
| `make reset-db` | Restaura as massas de dados de benchmark para estado limpo. |
| `make reset-db SYSTEMS=true` | Sobe/reinicia os containers Docker nas VMs Vagrant e restaura os bancos. |
| `make dashboard` | Inicia a interface web Streamlit em `http://localhost:8501`. |
| `make collect-boca` | Coleta métricas do SO (`sar`) via SSH na VM BOCA. |
| `make collect-helium` | Coleta métricas do SO (`sar`) via SSH na VM Helium. |
| `make load-boca` | Executa o Locust contra o BOCA (`http://192.168.56.11:8000`). |
| `make load-helium` | Executa o Locust contra o Helium (`http://192.168.56.10:8000`). |
| `make clean` | Limpa logs, arquivos temporários de resultados e a pasta `venv/`. |

---

## 🎯 Cenários de Estresse Suportados (`SCENARIO`)

Você pode alterar o perfil de carga passando a variável `SCENARIO`:

- `burst`: Pico instantâneo de submissões (ex: abertura de prova).
- `baseline`: Carga constante de 1 usuário por 2 minutos.
- `steady`: Carga contínua estável por 25 minutos.
- `ramp`: Degraus crescentes (ex: 10 → 25 → 50 → 100 usuários).
- `endurance`: Teste de longa duração para detectar vazamentos de memória (memory leaks).

Exemplo:
```bash
make load-helium SCENARIO=ramp USERS=50
```

---

## 📁 Estrutura de Diretórios do Projeto

```
jams/
├── Makefile                   # Automação principal de comandos
├── AGENTS.md                  # Especificação técnica e manifesto de arquitetura
├── Vagrantfile                # Definição e provisionamento das VMs Vagrant (boca e helium)
├── analysis/
│   ├── live_dashboard.py      # Live Dashboard Web em Streamlit + Plotly
│   └── requirements.txt       # Dependências da interface de observabilidade
├── loadgen/
│   ├── locustfile.py          # Script de carga Locust (BocaUser e HeliumUser)
│   ├── requirements.txt       # Dependências do gerador de carga
│   └── submissions/           # Massa de submissões idênticas (AC, WA, TLE, CE)
├── monitoring/
│   ├── sar-collect.sh         # Script de coleta de telemetria via Vagrant SSH
│   └── parse_sar.py           # Parser de relatórios sar para CSV
├── provisioning/
│   └── reset_databases.sh     # Script de automação para restauração de estado inicial
└── docs/
    └── MULTI_SERVICE_OBSERVABILITY.md # Catálogo completo de descoberta de serviços
```

---

## 📜 Licença

Este projeto é desenvolvido para fins de pesquisa, benchmarking e avaliação de sistemas de julgamento automático.
