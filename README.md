# ⚡ JAMS — Judge Assessment & Metrics Suite

> **Plataforma de Benchmark Comparativo e Observabilidade Multi-Serviço para Juízes Automáticos (BOCA vs Helium)**

O **JAMS** (*Judge Assessment & Metrics Suite*) é uma suíte de testes de carga, observabilidade em tempo real e telemetria de SO projetada para avaliar e comparar a performance, latência de julgamento e utilização de recursos entre diferentes plataformas de maratona de programação (**BOCA** e **Helium**) sob condições de hardware rigorosamente idênticas.

---

## 📐 Topologia da Arquitetura & Infraestrutura

O ambiente opera em duas máquinas virtuais gerenciadas pelo **Vagrant** (VirtualBox) via submódulo Git (`vagrant/`), cada uma provida com **2 vCPU / 2048 MB RAM** rodando **Ubuntu 22.04 LTS**:

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

- **Python 3.11+**
- **Vagrant** & **VirtualBox**
- **GNU Make**
- **Git**

---

## 🚀 Guia de Execução (Dois Fluxos de Uso)

### 🟢 Fluxo 1: Primeiríssima Vez (First-Time Setup)

Siga este passo a passo se você acabou de clonar o repositório em uma máquina nova:

```bash
# 1. Clonar o repositório incluindo os submódulos Git
git clone --recursive git@github.com:wennerl77/jams.git
cd jams

# 2. Instalar dependências Python em ambiente virtual isolado (venv/)
make setup

# 3. Subir e Provisionar as VMs Vagrant (Cria as VMs e executa os scripts de provisionamento)
make vm-up

# 4. Restaurar e Popular os Bancos de Dados em Estado Limpo de Paridade
make reset-db SYSTEMS=true

# 5. Iniciar o Live Dashboard Web em Tempo Real
make dashboard
```
Acesse no navegador: **`http://localhost:8501`**

---

### 🔵 Fluxo 2: Uso Diário (VMs Já Configuradas)

Siga este fluxo no dia a dia quando as máquinas virtuais Vagrant já foram criadas e provisionadas anteriormente:

```bash
# 1. Garantir que as VMs estão ligadas (início instantâneo)
make vm-up

# 2. (Opcional) Resetar o banco para uma nova rodada limpa de testes
make reset-db

# 3. Iniciar o Live Dashboard Web
make dashboard

# 4. Em outros terminais, iniciar a telemetria e o disparo de carga:

# Para o Helium:
make collect-helium SCENARIO=burst INTERVAL=1
make load-helium SCENARIO=burst USERS=10

# Para o BOCA:
make collect-boca SCENARIO=burst INTERVAL=1
make load-boca SCENARIO=burst USERS=10
```

---

## ⚙️ Matriz de Comandos Automáticos (`Makefile`)

| Comando | Descrição |
|---|---|
| `make setup` | Cria o ambiente virtual `venv/` e instala todas as dependências Python. |
| `make vm-up` | Inicializa submódulos, sobe as VMs Vagrant e roda os scripts de provisionamento. |
| `make vm-provision` | Força a re-execução dos scripts de provisionamento dentro das VMs. |
| `make vm-status` | Exibe o status atual das máquinas virtuais no Vagrant. |
| `make vm-down` | Desliga as VMs Vagrant para liberar recursos do host. |
| `make reset-db` | Restaura as massas de dados de benchmark para estado limpo. |
| `make reset-db SYSTEMS=true` | Inicia/garante os containers Docker nas VMs e restaura os bancos. |
| `make dashboard` | Inicia a interface web Streamlit em `http://localhost:8501`. |
| `make collect-boca` | Coleta métricas do SO (`sar`) via SSH na VM BOCA. |
| `make collect-helium` | Coleta métricas do SO (`sar`) via SSH na VM Helium. |
| `make load-boca` | Executa o Locust contra o BOCA (`http://192.168.56.11:8000`). |
| `make load-helium` | Executa o Locust contra o Helium (`http://192.168.56.10:8000`). |
| `make clean` | Limpa logs, arquivos temporários de resultados e a pasta `venv/`. |

---

## 🎯 Cenários de Estresse Suportados (`SCENARIO`)

Altere o perfil de carga passando a variável `SCENARIO`:

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
├── README.md                  # Documentação instrutiva do projeto
├── AGENTS.md                  # Especificação técnica e manifesto de arquitetura
├── vagrant/ @submodule        # Submódulo Git com Vagrantfile e scripts de provisionamento
│   ├── Vagrantfile
│   └── provision/
│       ├── boca.sh            # Provisionador automático do BOCA Docker
│       └── helium.sh          # Provisionador automático do Helium Docker
├── analysis/
│   ├── live_dashboard.py      # Live Dashboard Web em Streamlit + Plotly
│   └── requirements.txt       # Dependências da interface de observabilidade
├── loadgen/
│   ├── locustfile.py          # Script de carga Locust (BocaUser e HeliumUser)
│   └── submissions/           # Massa de submissões idênticas (AC, WA, TLE, CE)
├── monitoring/
│   ├── sar-collect.sh         # Script de coleta de telemetria via Vagrant SSH
│   └── parse_sar.py           # Parser de relatórios sar para CSV
└── provisioning/
    └── reset_databases.sh     # Script de automação para restauração de estado inicial
```

---

## 📜 Licença

Este projeto é desenvolvido para fins de pesquisa, benchmarking e avaliação de sistemas de julgamento automático.
