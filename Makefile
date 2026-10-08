# =============================================================================
# JAMS Benchmark Suite Makefile — Helium Controlled Edition
# =============================================================================

.PHONY: help setup install build up down ps logs \
	helium-build helium-up helium-down helium-ps helium-logs reset-db-helium \
	reset-db dashboard test-submission collect-helium load-helium clean \
	vm-up vm-down vm-status

# Resolve canonical root directory
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Select active Python virtual environment (prefers root venv, falls back to loadgen/venv)
ifneq ("$(wildcard $(ROOT_DIR)/venv/bin/python)","")
	VENV ?= $(ROOT_DIR)/venv
else
	VENV ?= $(ROOT_DIR)/loadgen/venv
endif

# Default Variables
SCENARIO ?= burst
INTERVAL ?= 1
USERS ?= 1
SPAWN_RATE ?= 1
PORT ?= 8501
FILE ?= ac_sum.cpp
ifeq ($(origin LANG),environment)
    LANG := cpp
endif
LANG ?= cpp
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit
LOCUST := $(VENV)/bin/locust
HELIUM_HOST ?= http://127.0.0.10:8000
DOCKER_COMPOSE ?= docker compose

COMPOSE_HELIUM := $(DOCKER_COMPOSE) -f docker-compose.yml

help: ## Exibe este menu de ajuda com os comandos disponíveis
	@echo "================================================================="
	@echo " JAMS Benchmark Suite - Comandos de Automação (Makefile)"
	@echo "================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo "================================================================="
	@echo " Exemplo de Uso:"
	@echo "   make setup"
	@echo "   make build"
	@echo "   make up"
	@echo "   make reset-db"
	@echo "   make dashboard"
	@echo "   make load-helium USERS=5 INTERVAL=2"
	@echo "================================================================="

# --- COMANDOS GLOBAIS ---


# --- CONFIGURAÇÃO & AMBIENTE ---

setup: install ## Instala todas as dependências Python em ambiente virtual isolado

$(VENV)/bin/activate:
	@echo "Criando ambiente virtual Python em $(VENV)..."
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate ## Instala dependências de analysis/ e loadgen/
	@echo "Instalando dependências Python no $(VENV)..."
	$(PIP) install --upgrade pip
	$(PIP) install -r $(ROOT_DIR)/analysis/requirements.txt
	$(PIP) install -r $(ROOT_DIR)/loadgen/requirements.txt
	@echo "✔ Dependências instaladas com sucesso no $(VENV)."

reset-db: ## Restaura o banco de dados do Helium (MySQL) em estado limpo de benchmark
	@echo "Resetando e populando o banco de dados do Helium (MySQL)..."
	$(ROOT_DIR)/provisioning/reset_databases.sh --helium

dashboard: $(VENV)/bin/activate ## Inicia o Live Dashboard Web em http://localhost:8501
	@echo "Limpando registros e dados anteriores de benchmark..."
	mkdir -p results/queue
	rm -rf results/helium/* results/queue/*
	@echo "Iniciando Live Dashboard Web em http://localhost:8501..."
	cd analysis && $(STREAMLIT) run live_dashboard.py --server.port=$(PORT) 2>&1 | tee -a ../results/dashboard.log

test-submission: $(VENV)/bin/activate ## Envia submissão de teste individual no Helium (FILE=ac_sum.cpp LANG=cpp)
	@echo "Enviando submissão de teste para Helium (FILE=$(FILE), LANG=$(LANG))..."
	$(PYTHON) loadgen/submitter.py --target helium --file $(FILE) --lang $(LANG)

collect-helium: ## Inicia coleta de telemetria de containers do Helium (SCENARIO=burst INTERVAL=1s)
	@echo "Iniciando telemetria Docker no Helium (SCENARIO=$(SCENARIO), INTERVAL=$(INTERVAL)s)..."
	./monitoring/sar-collect.sh helium $(SCENARIO) $(INTERVAL)

load-helium: $(VENV)/bin/activate ## Dispara carga Locust contra Helium ($(HELIUM_HOST))
	@echo "Disparando carga Locust no Helium ($(HELIUM_HOST))..."
	cd loadgen && TARGET_SYSTEM=helium SCENARIO=$(SCENARIO) $(LOCUST) -f locustfile.py --host=$(HELIUM_HOST)

clean: ## Limpa logs temporários, CSVs de resultados e arquivos transitórios
	@echo "Limpando arquivos de resultados temporários..."
	rm -rf results/helium/* results/queue/*
	@echo "✔ Limpeza concluída."

# Aliases de compatibilidade
vm-up: up ## Alias de compatibilidade para 'make up'
vm-down: down ## Alias de compatibilidade para 'make down'
vm-status: ps ## Alias de compatibilidade para 'make ps'
