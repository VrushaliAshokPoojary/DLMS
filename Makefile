.PHONY: up down logs ps test

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

test:
	python -m compileall backend/app
	npm --prefix frontend run build
