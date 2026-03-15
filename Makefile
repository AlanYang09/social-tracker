.PHONY: up down build logs ps shell-api shell-db reset

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

ps:
	docker compose ps

# Tail logs for a specific service: make logs-api
logs-%:
	docker compose logs -f $*

shell-api:
	docker compose exec api bash

shell-db:
	docker compose exec postgres psql -U tracker -d tracker

# Wipe DB volume and restart fresh
reset:
	docker compose down -v
	docker compose up --build -d
