# Topologia de Serviços Locais & Guia de Observabilidade Multi-Serviços

Este documento fornece o catálogo completo de descoberta de serviços (*service discovery catalog*) para as duas aplicações em teste de carga — **BOCA** e **Helium** —, cada uma executada de forma isolada em sua própria máquina virtual gerenciada pelo **Vagrant** no host local.

---

## 1. Visão Geral da Topologia Multi-Serviços

Ambas as máquinas virtuais operam na mesma rede privada do host (`192.168.56.0/24`) com provisão idêntica de hardware (2 vCPU / 2048 MB RAM) rodando Ubuntu 22.04 LTS (`ubuntu/jammy64`).

```
                              +-------------------------------------------+
                              |              HOST LOCAL                   |
                              |   Agente de Observabilidade Multi-Serviço  |
                              |     (Locust + Live Dashboard + sar)       |
                              +--------------------+----------------------+
                                                   |
                   +-------------------------------+-------------------------------+
                   |                                                               |
                   v (Vagrant SSH / HTTP :8000)                                    v (Vagrant SSH / HTTP :8000)
+--------------------------------------------------+   +--------------------------------------------------+
|                VM 1: boca                        |   |               VM 2: helium                       |
|         IP Privado: 192.168.56.11                |   |        IP Privado: 192.168.56.10                |
|        Provider: Vagrant (VirtualBox)            |   |       Provider: Vagrant (VirtualBox)             |
|                                                  |   |                                                  |
| - Serviços Docker:                               |   | - Serviços Docker:                               |
|   - boca-web (Apache + PHP) :8000->:80           |   |   - webserver (Nginx Alpine) :8000->:80, :8443   |
|   - boca-jail (AutoJudge Jail chroot)            |   |   - app (PHP 8.3-FPM + Laravel 12/13)            |
|   - boca-db (PostgreSQL 14) :5432                |   |   - db (MySQL 8.0) :3306                         |
|   - adminer (Web UI) :8080                       |   |   - redis (Redis 7 Cache & Queue) :6379          |
|                                                  |   |   - autojudge (Worker SYS_PTRACE)                |
| - Daemons do SO:                                 |   |   - queue (Laravel Queue Worker)                 |
|   - sysstat / sar daemon (Amostragem: 1s)        |   | - Daemons do SO:                                 |
|                                                  |   |   - sysstat / sar daemon (Amostragem: 1s)        |
+--------------------------------------------------+   +--------------------------------------------------+
```

---

## 2. Especificação Detalhada da VM BOCA (`boca`)

- **Identificador de VM no Vagrant**: `boca`
- **Endereço IP Estático**: `192.168.56.11`
- **Comando de Acesso e Inspeção**: `vagrant ssh boca`
- **Proprietário da Conexão SSH**: Gerenciado exclusivamente pelo Vagrant (`vagrant@192.168.56.11`).

### Catálogo de Serviços Docker (BOCA)

| Nome do Container | Função / Serviço | Porta Exposta no IP Privado | Logs Internos |
|---|---|---|---|
| `boca-web` | Servidor Web Apache + PHP | `8000` (`http://192.168.56.11:8000`) | `/var/log/apache2/access.log`<br>`/var/log/apache2/error.log` |
| `boca-jail` | Executor do Autojudge (chroot/jail) | Interna (Docker bridge) | `docker logs boca-jail` |
| `boca-db` | Banco de Dados PostgreSQL 14 | `5432` (`boca-db:5432`) | `/var/log/postgresql/` |
| `adminer` | Gerenciador Web DB (Dev) | `8080` (`http://192.168.56.11:8080`) | `docker logs adminer` |

### Endpoints de Verificação (BOCA)
- **Painel Principal**: `GET http://192.168.56.11:8000/index.php`
- **Autenticação**: `POST http://192.168.56.11:8000/index.php` (form `user/password`)
- **Submissão**: `POST http://192.168.56.11:8000/run.php` (multipart/form-data)

---

## 3. Especificação Detalhada da VM Helium (`helium`)

- **Identificador de VM no Vagrant**: `helium`
- **Endereço IP Estático**: `192.168.56.10`
- **Comando de Acesso e Inspeção**: `vagrant ssh helium`
- **Proprietário da Conexão SSH**: Gerenciado exclusivamente pelo Vagrant (`vagrant@192.168.56.10`).

### Catálogo de Serviços Docker (Helium)

| Nome do Container | Função / Serviço | Porta Exposta no IP Privado | Logs Internos |
|---|---|---|---|
| `webserver` | Servidor Web Nginx Alpine | `8000` (`http://192.168.56.10:8000`), `8443` | `/var/log/nginx/access.log`<br>`/var/log/nginx/error.log` |
| `app` | Aplicação PHP 8.3-FPM (Laravel) | Interna FPM :9000 | `/var/www/html/storage/logs/laravel.log` |
| `db` | Banco de Dados MySQL 8.0 | `3306` (`192.168.56.10:3306`) | `/var/log/mysql/error.log` |
| `redis` | Cache & Filas Redis 7 | `6379` (`192.168.56.10:6379`) | `docker logs redis` |
| `autojudge` | Worker Autônomo de Julgamento (`SYS_PTRACE`) | Interna | `docker logs autojudge` |
| `queue` | Laravel Queue Worker | Interna | `docker logs queue` |

### Endpoints de Verificação (Helium API REST)
- **Health Check**: `GET http://192.168.56.10:8000/api/health`
- **Contest Ativo**: `GET http://192.168.56.10:8000/api/contest/current`
- **Autenticação API**: `POST http://192.168.56.10:8000/api/login`
- **Submissão API**: `POST http://192.168.56.10:8000/api/runs` (Sanctum Bearer Token)
- **Consulta de Run**: `GET http://192.168.56.10:8000/api/runs/{id}`

---

## 4. Catálogo Declarativo JSON de Serviços (`service_catalog.json`)

Para integração autônoma com crawlers, monitores de observabilidade e agentes de IA, a especificação dos serviços está estruturada abaixo:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "environment": "local_vagrant_benchmark",
  "services": [
    {
      "id": "boca",
      "name": "BOCA Online Contest Administrator",
      "vagrant_vm": "boca",
      "ip": "192.168.56.11",
      "ssh_command": "vagrant ssh boca",
      "web_url": "http://192.168.56.11:8000",
      "auth_type": "cookie_session",
      "containers": [
        {"name": "boca-web", "port": 8000, "protocol": "http"},
        {"name": "boca-jail", "port": null, "protocol": "chroot_jail"},
        {"name": "boca-db", "port": 5432, "protocol": "postgresql"}
      ],
      "telemetry": {
        "sar_command": "vagrant ssh boca -c 'sar -u -r -b -w 1 60'",
        "output_raw": "results/boca/<scenario>/sar_raw.txt"
      }
    },
    {
      "id": "helium",
      "name": "Helium Contest System",
      "vagrant_vm": "helium",
      "ip": "192.168.56.10",
      "ssh_command": "vagrant ssh helium",
      "web_url": "http://192.168.56.10:8000",
      "auth_type": "sanctum_bearer_token",
      "containers": [
        {"name": "webserver", "port": 8000, "protocol": "http"},
        {"name": "app", "port": 9000, "protocol": "fastcgi"},
        {"name": "db", "port": 3306, "protocol": "mysql"},
        {"name": "redis", "port": 6379, "protocol": "redis"},
        {"name": "autojudge", "port": null, "protocol": "ptrace_worker"}
      ],
      "telemetry": {
        "sar_command": "vagrant ssh helium -c 'sar -u -r -b -w 1 60'",
        "output_raw": "results/helium/<scenario>/sar_raw.txt"
      }
    }
  ]
}
```
