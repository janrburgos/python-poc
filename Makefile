.PHONY: build
build:
	docker build --rm -t fastapi-local-app -f Dockerfile.dev .
	docker image prune -f

.PHONY: update
update:
	docker run --rm -v $(PWD):/app fastapi-local-app pipenv lock
	make build

.PHONY: dotEnvLocal
dotEnvLocal:
	cp .env-local .env

.PHONY: start
start:
	docker-compose up --detach db
	docker-compose run --rm fastapi-app pipenv run alembic upgrade head
	docker-compose run --name fastapi-app --rm --service-ports fastapi-app \
		pipenv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: shell
shell:
	docker exec -it fastapi-app bash

.PHONY: test
test:
	docker-compose down --volumes
	docker-compose up --detach db
	docker-compose run --rm fastapi-app pipenv run alembic upgrade head
	docker-compose run --name fastapi-app --rm fastapi-app \
		pipenv run pytest -vv --cov=app --cov-report=html  $(filter-out $@,$(MAKECMDGOALS))
	docker-compose down --volumes

.PHONY: format
format:
	docker run --rm -v $(PWD):/app fastapi-local-app pipenv run black .
	docker run --rm -v $(PWD):/app fastapi-local-app pipenv run ruff check . --fix

.PHONY: dbMigrate
dbMigrate:
	docker-compose up --detach db
	docker-compose run --rm fastapi-app pipenv run alembic upgrade head
	docker-compose run --rm fastapi-app pipenv run alembic revision --autogenerate -m "$(filter-out $@,$(MAKECMDGOALS))"
	docker-compose down
