.PHONY: up down logs ps build backend shell format lint

up:
	docker compose up -d

ps:
	docker compose ps

logs:
	docker compose logs -f backend frontend scanner ai-engine responder

build:
	docker compose build

backend:
	docker compose exec backend bash

shell:
	docker compose exec backend bash

format:
	docker compose exec backend bash -lc "ruff format . && ruff check . --fix"

lint:
	docker compose exec backend bash -lc "ruff check ."

down:
	docker compose down -v
