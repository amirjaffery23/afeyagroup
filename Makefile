PROJECT_NAME = stock-dashboard
COMPOSE = docker-compose

ENV ?= dev
ENV_FILE = .env.$(ENV)
PROFILES = --profile $(ENV)

up:
	@echo ">> Starting with env: $(ENV_FILE)"
	$(COMPOSE) --env-file $(ENV_FILE) $(PROFILES) up -d

down:
	$(COMPOSE) --env-file $(ENV_FILE) down

restart:
	$(MAKE) down ENV=$(ENV)
	$(MAKE) up ENV=$(ENV)

build:
	$(COMPOSE) --env-file $(ENV_FILE) $(PROFILES) build

logs:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f

ps:
	$(COMPOSE) --env-file $(ENV_FILE) ps

prune:
	docker system prune -a --volumes -f

shell:
	$(COMPOSE) --env-file $(ENV_FILE) exec backend /bin/bash

clean:
	docker-compose --env-file .env.$(ENV) down --remove-orphans || true
	docker rm -f $$(docker ps -aq) || true
	docker network prune -f
	
clean_volumes:
	docker volume ls -qf dangling=true | grep -v afeyagroup_stock_data | xargs -r docker volume rm


