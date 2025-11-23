# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

.DEFAULT:
	@$(MAKE) -s help

.PHONY: help
help:
	@echo ''
	@echo 'Available commands :'
	@echo '  ${YELLOW}make tests${RESET}     : ${GREEN}Run unit tests script${RESET}'
	@echo '  ${YELLOW}make dev${RESET}       : ${GREEN}Run dev compose${RESET}'
	@echo '  ${YELLOW}make docker-start${RESET} : ${GREEN}Build Docker image and start container${RESET}'
	@echo '  ${YELLOW}make test-native-ci${RESET} : ${GREEN}Run unit tests script${RESET}'
	@echo ''

.PHONY: all
all: dev tests


###################
# DEV
.PHONY: dev
dev:
	@echo "Starting the dev compose"
	docker compose -f dev/docker-compose.dev.yaml up --build

###################
# TESTS
.PHONY: tests
tests:
	@echo "Starting test environment"
	cd tests; bash ./run_unit_tests.sh 

###################
# TESTS NATIVE to run smoothly on CI
.PHONY: tests-native-ci
tests-native-ci:
	@echo "1. Installation des dépendances..."
	pip install -r requirements.txt
	@echo "2. Import des données MongoDB..."
	# On suppose que l'hôte mongo est défini par MONGO_HOST (par défaut localhost)
	mongoimport --host $(or $(MONGO_HOST),localhost) --db test --collection boxes --type json --file tests/mongodb-import/test.boxes.json --jsonArray
	@echo "3. Démarrage de l'API en arrière-plan..."
	# On lance l'app et on stocke le PID pour le tuer à la fin
	set -a && . ./tests/.env.tests && set +a && \
	if [ -n "$$MONGO_URI" ]; then export DB_URI="$$MONGO_URI"; fi && \
	python3 -m hermes.main & echo $$! > hermes.pid
	sleep 5 # Attente barbare mais efficace que l'API démarre
	@echo "4. Lancement des tests..."
	# Définition des variables d'env identiques au docker-compose
	set -a && . ./tests/.env.tests && set +a && \
	cd tests && ./unit_tests.sh || (kill `cat ../hermes.pid` && rm ../hermes.pid && exit 1)
	@echo "5. Nettoyage..."
	kill `cat hermes.pid` && rm hermes.pid

###################
# DOCKER-START
.PHONY: compose-start
docker-start:
	@echo "Starting the compose"
	docker compose up --build
