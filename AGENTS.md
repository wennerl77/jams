# Stack Tecnológica & Especificação de Benchmark — BOCA vs Helium

> **Instruções para Agentes e Desenvolvedores**:  
> Este documento serve como referência técnica primária para qualquer agente ou engenheiro que opere neste repositório. O objetivo do projeto é testar, avaliar e comparar a performance, latência de julgamento e utilização de recursos entre o **BOCA Online Contest Administrator** e o **Helium (MicroHelium)** em condições de teste idênticas e reprodutíveis.

---

## Visão Geral

Um gerador de carga externo baseado em **Locust** envia submissões concorrentes para duas máquinas virtuais Vagrant idênticas (2 vCPU / 2GB RAM cada) em execução no mesmo host:
- Uma VM executando o ecossistema do **BOCA**.
- Uma VM executando o ecossistema do **Helium**.

Agentes de monitoramento em cada VM (`sysstat`/`sar`) registram uso de recursos em nível de sistema operacional e kernel a cada 1 segundo. Todos os dados convergem para o host (ou analisador Jupyter/pandas) para gerar métricas comparativas lado a lado.

```
                  +----------------------------------------------+
                  |                 HOST (Loadgen)               |
                  |  Locust Runner (Python 3.11+) + sar-collect  |
                  +-----------------------+----------------------+
                                          |
             +----------------------------+----------------------------+
             |                                                         |
             v (HTTP / 192.168.56.11:8000)                             v (HTTP / 192.168.56.10:8000)
+------------------------------------------+   +------------------------------------------+
|            VM BOCA (Vagrant)             |   |           VM HELIUM (Vagrant)            |
|       IP: 192.168.56.11 | 2 vCPU / 2GB   |   |       IP: 192.168.56.10 | 2 vCPU / 2GB   |
|                                          |   |                                          |
| - Docker Compose:                        |   | - Docker Compose:                        |
|   - boca-web (Apache + PHP) :8000->:80   |   |   - webserver (Nginx) :8000->:80, :8443  |
|   - boca-jail (AutoJudge Jail chroot)    |   |   - app (PHP 8.3-FPM, Laravel)           |
|   - boca-db (PostgreSQL 14)              |   |   - db (MySQL 8.0) :3306                 |
|   - adminer (dev) :8080                  |   |   - redis (Cache & Queue) :6379          |
|                                          |   |   - autojudge (Worker SYS_PTRACE)        |
| - sysstat (sar daemon / 1s sampling)     |   |   - queue worker & scheduler             |
+------------------------------------------+   | - sysstat (sar daemon / 1s sampling)     |
                                               +------------------------------------------+
```

---

## 1. Camada de Orquestração e Virtualização

| Item | Especificação |
|---|---|
| **Ferramenta de VM** | Vagrant com provider VirtualBox |
| **Box Base** | `ubuntu/jammy64` (Ubuntu 22.04 LTS) — mesma versão de SO e kernel em ambas as VMs para eliminar viés de benchmarking |
| **Hardware por VM** | 2 vCPU, 2048 MB RAM cada |
| **Topologia de Rede** | `private_network` (Host-Only Adapter) com IPs estáticos dedicados |

### Endereçamento de Rede e Mapeamento de Portas

Como as VMs operam em IPs privados distintos na interface de rede privada, **não há conflito de portas** mesmo utilizando a porta externa 8000 para ambas:

| Ambiente | IP Privado | Serviço Web Principal | Portas Adicionais / Ferramentas Dev |
|---|---|---|---|
| **Helium** | `192.168.56.10` | `http://192.168.56.10:8000` (Nginx/HTTP) | `8443` (HTTPS)<br>`5173` (Vite Frontend Dev)<br>`8080` (phpMyAdmin opcional)<br>`8025` (Mailpit WebUI opcional)<br>`3306` (MySQL interno)<br>`6379` (Redis interno) |
| **BOCA** | `192.168.56.11` | `http://192.168.56.11:8000` (Apache/PHP BOCA) | `8080` (Adminer DB WebUI em dev)<br>`5432` (PostgreSQL 14 interno `boca-db`) |
| **Loadgen** | Host (ou IP `192.168.56.13`) | Locust Master/Worker | Dashboard web do Locust: `http://localhost:8089` |

### 1.1 Descoberta de Serviços Locais e Observabilidade Multi-Serviço

Ambas as aplicações (**BOCA** e **Helium**) rodam localmente no host do desenvolvedor, isoladas em suas próprias VMs gerenciadas pelo **Vagrant**. 

Para permitir que agentes externos de IA e ferramentas de telemetria identifiquem dinamicamente os contêineres Docker, logs internos e portas expostas em cada VM, consulte o guia detalhado e o catálogo estruturado JSON em:

👉 **[docs/MULTI_SERVICE_OBSERVABILITY.md](file:///home/wenner/Documents/carga-helium-boca/docs/MULTI_SERVICE_OBSERVABILITY.md)**

---

## 2. Especificação da VM BOCA

- **Sistema Operacional**: Ubuntu 22.04 LTS (`ubuntu/jammy64`).
- **Arquitetura de Aplicação**:
  - `boca-web`: Servidor Apache com PHP e suporte `php-pgsql`. Porta Host `8000` mapeada para a porta `80` interna do container.
  - `boca-jail`: Módulo autojudge em container privilegiado com controle de isolamento chroot/jail.
  - `boca-db`: PostgreSQL 14 Alpine (porta padrão 5432).
  - `adminer`: Interface de gerenciamento de banco (porta 8080 em modo dev).
- **Interface de Integração**:
  - **Sem API REST**: O BOCA não expõe rotas REST/JSON. O fluxo é inteiramente baseado em sessões de cookies (`PHPSESSID`), formulários HTML tradicionais e requisições `multipart/form-data`.
  - **Autenticação**: Submissão de credenciais para `index.php` armazenando cookies de sessão.
  - **Submissões**: `POST` multipart contendo arquivo fonte, problema, linguagem e contest ID.
  - **Polling de Veredito**: Requisições periódicas a `run.php` com parsing do HTML retornado para identificar a transição de estado da submissão (de *pending/judging* para veredito final: AC, WA, TLE, etc.).
- **Monitoramento**: Pacote `sysstat` ativo gravando métricas do sistema a cada 1s.

---

## 3. Especificação da VM Helium (MicroHelium)

- **Sistema Operacional**: Ubuntu 22.04 LTS (`ubuntu/jammy64`).
- **Arquitetura de Aplicação**:
  - `webserver`: Nginx (Alpine) roteando tráfego HTTP na porta `8000` (e SSL na `8443`).
  - `app`: PHP 8.3-FPM rodando o framework Laravel 12.x/13.x.
  - `db`: MySQL 8.0 (porta 3306).
  - `redis`: Redis 7 Alpine (porta 6379) gerenciando cache e filas assíncronas.
  - `queue`: Worker de background (`php artisan queue:work --sleep=3 --tries=3 --max-time=3600`).
  - `autojudge`: Worker de julgamento autônomo em container dedicado com `privileged: true` e permissão `SYS_PTRACE` (`php artisan autojudge:start --sleep=5`).
- **Interface de Integração**:
  - **API REST / JSON Nativa**: O Helium disponibiliza endpoints estruturados para contest, submissões e julgamento.
  - **Autenticação**: Laravel Sanctum Personal Access Token (`Authorization: Bearer <token>`).
  - **Endpoints Principais**:
    - `POST /api/runs`: Envio de submissão via `multipart/form-data` com campos `contest_id`, `problem_id`, `language_id`, `source_file`. Responde status HTTP `201 Created` com payload JSON contendo o objeto do Run criado.
    - `GET /api/runs/{id}`: Consulta do status e veredito do Run (`pending`, `judged`, answer).
    - `GET /api/runs?contest_id={id}`: Listagem paginada de runs do usuário/contest.
    - `GET /api/health`: Health check da API.
    - `GET /api/contest/current`: Metadados do contest ativo.
  - **Vantagem de Benchmark**: Elimina overhead e fragilidade de parsing HTML no teste de carga.
- **Monitoramento**: Pacote `sysstat` ativo gravando métricas do sistema a cada 1s.

---

## 4. Máquina de Carga (Loadgen)

- **Local de Execução**: Host principal (ou VM dedicada `loadgen` com specs enxutas).
- **Isolamento de Recursos**: O gerador de carga **nunca** deve ser executado de dentro da VM de teste (`boca` ou `helium`), impedindo que o uso de CPU/memória do Locust interfira nas métricas da aplicação alvo.
- **Stack do Loadgen**:
  - Python 3.11+
  - Locust ≥ 2.31
  - Requests / HTTPX
  - BeautifulSoup4 (para parsing dos formulários e tabelas do BOCA)
  - pandas, numpy, matplotlib / seaborn / jupyter (para análise e consolidação)

---

## 5. Observabilidade e Telemetria

### Coleta com `sar` (`sysstat`)
Durante as janelas de benchmark, o script de telemetria dispara em cada VM:
```bash
sar -u -r -b -w 1 > /tmp/sar_benchmark_<cenario>_<timestamp>.txt
```
- `-u`: Utilização de CPU (%user, %system, %iowait, %idle).
- `-r`: Memória (%memused, buffers, cached).
- `-b`: Taxa de I/O de blocos de disco (tps, rtps, wtps).
- `-w`: Troca de contexto e criação de processos (`cswch/s`, `proc/s`).

Os dados são convertidos para CSV ao término da rodada e sincronizados para `results/<target>/<scenario>/sar_metrics.csv`.

---

## 6. Especificação de Implementação do Locust

### 6.1 Objetivos de Medição

O Locust mede três dimensões fundamentais:
1. **Latência de Aceite HTTP**: Tempo de resposta do POST da submissão (tempo até o servidor web receber o arquivo e devolver 200/201).
2. **Tempo Total de Julgamento (Assíncrono)**: Do momento do envio até o veredito definitivo sair da fila do auto-judge.
3. **Throughput e Taxa de Erro**: Número de submissões processadas por minuto e estabilidade sob picos de estresse.

### 6.2 Métrica Customizada de Julgamento

Para não mesclar a latência HTTP com o tempo assíncrono de compilação/sandboxing, o `locustfile.py` emite um evento sintético:
```python
events.request.fire(
    request_type="JUDGE",
    name="submission_to_verdict",
    response_time=verdict_latency_ms,
    response_length=0,
    exception=None,
    context=None
)
```
Isso separa claramente nos relatórios do Locust:
- `POST /run` (HTTP Network & Webserver throughput).
- `JUDGE submission_to_verdict` (Eficiência do motor de execução e filas do juiz).

### 6.3 Matriz de Perfis de Carga (`LoadTestShape`)

Controlado via variável de ambiente `SCENARIO`:

| Cenário | Comportamento | Objetivo do Teste |
|---|---|---|
| `baseline` | 1 usuário constante por 2 min | Estabelecer o consumo de repouso e latência mínima sem contenção |
| `steady` | N usuários estáveis por 25 min | Avaliar performance em regime permanente de contest |
| `burst` | Subida instantânea de 100% dos usuários em < 1 min | Simular abertura de prova ou encerramento de freeze |
| `ramp` | Degraus crescentes (ex: 10 -> 25 -> 50 -> 100 usuários) | Identificar ponto de inflexão e saturação de hardware |
| `endurance` | Carga constante moderada por horas | Detectar vazamentos de memória (memory leaks), zumbis ou degradação |

### 6.4 Massa de Testes Controlada

O diretório `loadgen/submissions/` deve conter códigos fonte idênticos testados em ambas as plataformas:
- `ac_sum.cpp` / `ac_sum.py`: Solução que deve resultar em Accepted.
- `wa_sum.cpp` / `wa_sum.py`: Solução incorreta (Wrong Answer).
- `tle_loop.cpp` / `tle_loop.py`: Solução com loop infinito (Time Limit Exceeded).
- `ce_syntax.cpp` / `ce_syntax.py`: Solução com erro de compilação (Compilation Error).

---

## 7. Estrutura de Diretórios do Repositório

```
carga-helium-boca/
├── AGENTS.md                   # Este manifesto de arquitetura e instruções
├── Vagrantfile                 # Definição e provisionamento das VMs (boca e helium)
├── contracts/                  # Especificação declarativa de contratos JSON para paridade
│   ├── boca/                   # Contratos com chaves do PostgreSQL / BOCA (contest, problem, user, language, submission)
│   └── helium/                 # Contratos com chaves do MySQL / Laravel Helium (contest, problem, user, language, submission)
├── provisioning/               # Scripts de seeders e reset dos bancos de dados
│   ├── boca/01_seed_benchmark.sql     # Seed SQL do PostgreSQL para o BOCA
│   ├── helium/01_seed_benchmark.sql   # Seed SQL do MySQL para o Helium
│   └── reset_databases.sh             # Script de automação para restauração de estado inicial
├── loadgen/
│   ├── locustfile.py           # Script principal do Locust (BaseJudgeUser, BocaUser, HeliumUser)
│   ├── requirements.txt        # Dependências Python (locust, beautifulsoup4, etc.)
│   ├── .env.example            # Template de variáveis (hosts, portas, credenciais, tokens)
│   ├── scenarios/              # Perfis do DynamicShape para cada teste
│   └── submissions/            # Códigos-fonte de teste (AC, WA, TLE, CE)
│       ├── cpp/
│       └── python/
├── monitoring/
│   ├── sar-collect.sh          # Script de disparo e coleta de sar nas VMs via SSH
│   └── parse_sar.py            # Conversor de saídas de texto do sar para CSV
├── results/
│   ├── boca/                   # CSVs e relatórios HTML do BOCA organizados por cenário
│   └── helium/                 # CSVs e relatórios HTML do Helium organizados por cenário
└── analysis/
    ├── live_dashboard.py       # Dashboard Web Dinâmico em tempo real (Streamlit + Plotly)
    ├── requirements.txt        # Dependências do Dashboard (streamlit, plotly, pandas)
    ├── compare.ipynb           # Notebook Jupyter com gráficos comparativos de latência e CPU/RAM
    └── export_report.py        # Script para gerar relatório final consolidado
```

### 7.1 Como Iniciar o Dashboard Dinâmico em Tempo Real

```bash
cd analysis
pip install -r requirements.txt
streamlit run live_dashboard.py --server.port=8501
```
Acesse `http://localhost:8501` no navegador. O dashboard permite alternar em tempo real entre a visão **"⚔️ Comparativo Lado a Lado"**, **"🟢 Apenas BOCA"** ou **"🔵 Apenas Helium"**.

---

## 8. Como Executar os Benchmarks

### Método Simplificado via `Makefile` (Recomendado)

```bash
# 1. Instalar dependências de todos os componentes
make setup

# 2. Resetar e popular os bancos de dados em estado limpo de paridade
make reset-db

# 3. Iniciar o Live Dashboard Web em http://localhost:8501
make dashboard

# 4. Iniciar a telemetria (Terminal 2) e a carga no BOCA (Terminal 3)
make collect-boca SCENARIO=burst
make load-boca SCENARIO=burst

# 5. Iniciar a telemetria (Terminal 2) e a carga no Helium (Terminal 3)
make collect-helium SCENARIO=burst
make load-helium SCENARIO=burst
```

### Método Manual (CLI Direta)

```bash
# 1. Preparar o ambiente de carga
cd loadgen
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Execução no BOCA (Cenário burst, modo headless)
TARGET=boca SCENARIO=burst locust -f locustfile.py \
  --host=http://192.168.56.11:8000 --headless \
  --csv=../results/boca/burst --html=../results/boca/burst.html

# 3. Execução no Helium (Cenário burst, modo headless)
TARGET=helium SCENARIO=burst locust -f locustfile.py \
  --host=http://192.168.56.10:8000 --headless \
  --csv=../results/helium/burst --html=../results/helium/burst.html
```

> **Regra Estatística**: Repita cada cenário no mínimo **3 vezes** para cada alvo, descartando outliers e calculando médias com desvio padrão.

---

## 9. Diretrizes e Regras Operacionais para Agentes de IA

1. **Paridade Rigorosa**: Nunca compare cenários com números de vCPUs ou memória diferentes. As VMs devem permanecer com 2 vCPU / 2048 MB.
2. **Ambiente Limpo Pré-Teste**: Antes de iniciar uma bateria de testes, limpe submissões antigas das filas e reinicie os containers ou serviços de autojudge para evitar viés de aquecimento de cache desbalanceado.
3. **Não poluir as VMs com o Gerador**: Nunca execute o Locust dentro da VM `boca` ou `helium`. O Locust consome CPU considerável para gerar tráfego HTTP concorrente e deve rodar externamente.
4. **Isolamento de Variáveis**: Mantenha os mesmos arquivos de submissão (mesmos bytes, mesmos algoritmos) em ambos os sistemas.
