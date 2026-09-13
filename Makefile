# =============================================================================
# Benchmark Suite Makefile (BOCA vs Helium)
# =============================================================================

.PHONY: help setup install reset-db start-systems dashboard collect-boca collect-helium load-boca load-helium clean submodule-init vm-up vm-provision vm-down vm-status

# Default Variables
SCENARIO ?= burst
INTERVAL ?= 1
USERS ?= 1
SPAWN_RATE ?= 1
PORT ?= 8501
SYSTEMS ?= false
VENV ?= venv
PYTHON ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip
STREAMLIT ?= $(VENV)/bin/streamlit
LOCUST ?= $(VENV)/bin/locust
VAGRANT_DIR ?= vagrant

help: ## Exibe este menu de ajuda com os comandos disponíveis
	@echo "================================================================="
	@echo " Benchmark Suite - Comandos de Automação (Makefile)"
	@echo "================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo "================================================================="
	@echo " Exemplo de Uso:"
	@echo "   make setup"
	@echo "   make vm-up"
	@echo "   make reset-db SYSTEMS=true"
	@echo "   make dashboard"
	@echo "   make load-boca SCENARIO=burst USERS=10"
	@echo "================================================================="

submodule-init: ## Garante que os submódulos Git (vagrant/) estejam clonados
	@if [ ! -f $(VAGRANT_DIR)/Vagrantfile ]; then \
		echo "Inicializando submódulo Git (vagrant/)..."; \
		git submodule update --init --recursive; \
	fi

vm-up: submodule-init ## Sobe as VMs Vagrant (boca e helium) e executa o provisionamento
	@echo "Iniciando VMs Vagrant e provisionando containers BOCA e Helium..."
	cd $(VAGRANT_DIR) && vagrant up

vm-provision: submodule-init ## Re-executa os scripts de provisionamento nas VMs Vagrant
	@echo "Forçando re-provisionamento das VMs Vagrant..."
	cd $(VAGRANT_DIR) && vagrant provision

vm-down: ## Desliga as máquinas virtuais Vagrant
	@echo "Desligando VMs Vagrant..."
	cd $(VAGRANT_DIR) && vagrant halt

vm-status: ## Exibe o status atual das máquinas virtuais Vagrant
	@if [ -d $(VAGRANT_DIR) ]; then \
		cd $(VAGRANT_DIR) && vagrant status; \
	else \
		vagrant status; \
	fi

setup: install ## Instala todas as dependências Python em ambiente virtual (venv/)

$(VENV)/bin/activate:
	@echo "Criando ambiente virtual Python (venv)..."
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate ## Instala dependências de analysis/ e loadgen/ no venv
	@echo "Instalando dependências de analysis/ e loadgen/ em $(VENV)..."
	$(PIP) install --upgrade pip
	$(PIP) install -r analysis/requirements.txt
	$(PIP) install -r loadgen/requirements.txt
	@echo "✔ Dependências instaladas com sucesso no ambiente virtual ($(VENV))."

reset-db: ## Restaura os bancos de dados (Adicione SYSTEMS=true para subir Docker nas VMs)
	@echo "Resetando e populando os bancos de dados..."
ifeq ($(SYSTEMS),true)
	./provisioning/reset_databases.sh --systems
else
	./provisioning/reset_databases.sh
endif

start-systems: ## Executa explicitamente 'docker compose up -d' dentro das VMs Vagrant
	@echo "Subindo containers Docker nas VMs Vagrant via --systems..."
	./provisioning/reset_databases.sh --systems

dashboard: $(VENV)/bin/activate ## Inicia o Live Dashboard Web em http://localhost:8501
	@echo "Iniciando Live Dashboard Web em http://localhost:8501..."
	cd analysis && ../$(STREAMLIT) run live_dashboard.py --server.port=$(PORT)

collect-boca: ## Inicia a coleta de telemetria sar via Vagrant SSH na VM BOCA (boca)
	@echo "Iniciando coleta de telemetria no BOCA (SCENARIO=$(SCENARIO), INTERVAL=$(INTERVAL)s)..."
	./monitoring/sar-collect.sh boca $(SCENARIO) $(INTERVAL)

collect-helium: ## Inicia a coleta de telemetria sar via Vagrant SSH na VM Helium (helium)
	@echo "Iniciando coleta de telemetria no Helium (SCENARIO=$(SCENARIO), INTERVAL=$(INTERVAL)s)..."
	./monitoring/sar-collect.sh helium $(SCENARIO) $(INTERVAL)

load-boca: $(VENV)/bin/activate ## Dispara o gerador de carga Locust contra a VM BOCA (192.168.56.11:8000)
	@echo "Disparando carga Locust no BOCA (http://192.168.56.11:8000)..."
	cd loadgen && TARGET_SYSTEM=boca SCENARIO=$(SCENARIO) ../$(LOCUST) -f locustfile.py --host=http://192.168.56.11:8000

load-helium: $(VENV)/bin/activate ## Dispara o gerador de carga Locust contra a VM Helium (192.168.56.10:8000)
	@echo "Disparando carga Locust no Helium (http://192.168.56.10:8000)..."
	cd loadgen && TARGET_SYSTEM=helium SCENARIO=$(SCENARIO) ../$(LOCUST) -f locustfile.py --host=http://192.168.56.10:8000

clean: ## Limpa logs temporários, CSVs de resultados e o ambiente virtual
	@echo "Limpando arquivos de resultados e ambiente virtual..."
	rm -rf results/boca/* results/helium/* $(VENV)
	@echo "✔ Limpeza concluída."

