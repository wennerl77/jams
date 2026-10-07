# Topologia de Serviços Locais & Guia de Observabilidade Multi-Serviço da Stack Helium (Docker Compose)

Este documento fornece o catálogo completo de descoberta de serviços (*service discovery catalog*) e o guia de observabilidade multi-serviço para a plataforma **Helium (MicroHelium)**, executada sob **Docker Compose** nativo com cota estrita de recursos (2.0 vCPU / 2048 MB RAM total) no host local Linux.

---

## 1. Visão Geral da Topologia Multi-Serviço

A stack opera isolada em bridge Docker dedicada (`helium-net`, MTU 1500), vinculada ao endereço IP de loopback `127.0.0.10`:

```
                              +-------------------------------------------+
                              |              HOST LOCAL                   |
                              |   Agente de Observabilidade Multi-Serviço |
                              |   (Locust + Live Dashboard + Telemetria)  |
                              +--------------------+----------------------+
                                                   |
                                                   v HTTP :8000 / HTTPS :8443
+---------------------------------------------------------------------------------+
|                              Stack Helium (Docker)                              |
|                       IP Local: 127.0.0.10 | 2.0 vCPU / 2GB                     |
|                                                                                 |
| - helium-webserver (Nginx Alpine) :8000, :8010, :8443                           |
| - helium-app (PHP 8.3-FPM + Laravel 12/13) FastCGI :9000                        |
| - helium-db (MySQL 8.0) :3306, :3307                                            |
| - helium-redis (Redis 7 Cache & Queue) :6379, :6380                             |
| - helium-autojudge (Worker SYS_PTRACE SafeExec)                                 |
|                                                                                 |
| Rede: helium-net (172.28.2.0/24)                                                |
| Telemetria: cgroups v2 / docker stats a cada 1s                                 |
+---------------------------------------------------------------------------------+
```

---

## 2. Especificação Detalhada da Stack Helium (MicroHelium)

- **Arquivo Docker Compose**: `docker-compose.helium.yml` (ou `docker-compose.yml`)
- **Endereço IP de Loopback**: `127.0.0.10`
- **Rede Docker**: `helium-net` (`172.28.2.0/24`)
- **Limites de Recursos Consolidados**: 2.00 vCPU, 2048 MB RAM, BlkIO Weight 500, 0 GPU, sem swap.

### Catálogo de Containers (Helium)

| Nome do Container | Função / Serviço | Recursos CGroup | Porta Exposta no Host | Logs Internos |
|---|---|---|---|---|
| `helium-webserver` | Servidor Web Nginx Alpine | 0.20 vCPU / 128 MB | `127.0.0.10:8000` (e `8010`), `8443` | `/var/log/nginx/access.log` |
| `helium-app` | Aplicação Laravel (PHP 8.3-FPM) | 0.25 vCPU / 320 MB | Interna FastCGI `:9000` | `/var/www/html/storage/logs/laravel.log` |
| `helium-db` | Banco de Dados MySQL 8.0 | 0.50 vCPU / 512 MB | `127.0.0.10:3306` (e `3307`) | `docker logs helium-db` |
| `helium-redis` | Cache e Filas Redis 7 Alpine | 0.05 vCPU / 64 MB | `127.0.0.10:6379` (e `6380`) | `docker logs helium-redis` |
| `helium-autojudge` | Worker de Julgamento (`SYS_PTRACE`, safeexec) | 1.00 vCPU / 1024 MB | Interna (`helium-net`) | `docker logs helium-autojudge` |

### Endpoints Principais (Helium REST API)
- **Health Check**: `GET http://127.0.0.10:8000/api/health`
- **Autenticação**: `POST http://127.0.0.10:8000/api/login` (JSON: `{"username": "...", "password": "..."}`)
- **Submissão**: `POST http://127.0.0.10:8000/api/runs` (`Authorization: Bearer <token>`)
- **Consulta de Veredito**: `GET http://127.0.0.10:8000/api/runs/{id}` (JSON Run Object)

---

## 3. Observabilidade Multi-Serviço por Camada

A observabilidade em tempo real é estruturada para monitorar os gargalos em cada elo da cadeia de atendimento:

1. **Camada Web (Nginx)**:
   - Taxa de requisições por segundo (RPS) e latência de roundtrip HTTP.
   - Códigos de status HTTP (2xx, 4xx, 5xx) e conexões simultâneas ativas.
2. **Camada de Aplicação (PHP-FPM / Laravel)**:
   - Tempo de resposta dos controllers da API REST (`/api/runs`, `/api/login`).
   - Saturação dos workers do PHP-FPM sob rajadas de submissão.
3. **Camada de Filas & Cache (Redis)**:
   - Tamanho da fila de submissões pendentes de julgamento (`runs_queue`).
   - Latência de leitura e escrita em cache de tokens e sessões.
4. **Camada de Julgamento (Autojudge Worker)**:
   - Tempo de compilação de código-fonte (`g++`, `gcc`, etc.).
   - Tempo de execução em sandbox seguro (`safeexec`) com `SYS_PTRACE`.
   - Latência total de veredito (tempo entre envio do run e emissão do resultado final).
5. **Camada de Persistência (MySQL 8.0)**:
   - Utilização de conexões e tempo de escrita de transações de runs e vereditos.
   - Consumo de CPU e I/O durante rajadas intensas.

---

## 4. Catálogo Declarativo JSON de Serviços (`service_catalog.json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "environment": "docker_compose_load_test",
  "resource_limits": {
    "total_cpus": 2.0,
    "total_ram_mb": 2048,
    "swap": "disabled",
    "gpu": "disabled",
    "io_weight": 500
  },
  "services": [
    {
      "id": "helium",
      "name": "Helium Contest System (MicroHelium)",
      "ip": "127.0.0.10",
      "web_url": "http://127.0.0.10:8000",
      "auth_type": "sanctum_bearer_token",
      "containers": [
        {"name": "helium-webserver", "role": "web", "cpus": 0.2, "ram_mb": 128, "port": 8000},
        {"name": "helium-app", "role": "app", "cpus": 0.25, "ram_mb": 320, "port": 9000},
        {"name": "helium-db", "role": "db", "cpus": 0.5, "ram_mb": 512, "port": 3306},
        {"name": "helium-redis", "role": "cache_queue", "cpus": 0.05, "ram_mb": 64, "port": 6379},
        {"name": "helium-autojudge", "role": "judge", "cpus": 1.0, "ram_mb": 1024, "port": null}
      ],
      "telemetry": {
        "collector": "monitoring/docker-collect.py helium <scenario>",
        "output_csv": "results/helium/<scenario>/sar_metrics.csv"
      }
    }
  ]
}
```
