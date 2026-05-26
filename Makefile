.PHONY: help tree status up down restart ps logs clean

help:
	@echo "Available commands:"
	@echo "  make tree      Show project folder structure"
	@echo "  make status    Show git status"
	@echo "  make up        Start local Docker services"
	@echo "  make down      Stop local Docker services"
	@echo "  make restart   Restart local Docker services"
	@echo "  make ps        Show running Docker services"
	@echo "  make logs      Show Docker logs"
	@echo "  make clean     Stop services and remove volumes"

tree:
	tree -L 3

status:
	git status

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d

ps:
	docker compose ps

logs:
	docker compose logs -f

clean:
	docker compose down -v
