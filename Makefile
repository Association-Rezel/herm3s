# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

.DEFAULT:
	@$(MAKE) -s help

.PHONY: help
help:
	@echo ''
	@echo 'Availaible commands :'
	@echo '  ${YELLOW}make tests${RESET}     : ${GREEN}Run unit tests script${RESET}'
	@echo '  ${YELLOW}make dev${RESET}       : ${GREEN}Run dev compose${RESET}'
	@echo '  ${YELLOW}make docker-start${RESET} : ${GREEN}Build Docker image and start container${RESET}'
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
# DOCKER-START
.PHONY: compose-start
docker-start:
	@echo "Starting the compose"
	docker compose up --build