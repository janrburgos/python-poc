.PHONY: build
build:
	docker build --rm -t fastapi-local-app -f Dockerfile.dev .
	docker image prune -f

.PHONY: update
update:
	docker run --rm -v $(PWD):/app fastapi-local-app pipenv lock

.PHONY: dotEnvLocal
dotEnvLocal:
	cp .env-local .env

.PHONY: start
start:
	docker run --rm --name fastapi-app -p 8000:8000 \
		-v $(PWD):/app \
		fastapi-local-app \
		pipenv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: shell
shell:
	docker exec -it fastapi-app bash

.PHONY: test
test:
	docker run --rm -v $(PWD):/app fastapi-local-app pipenv run pytest -vv --cov=app --cov-report=html  $(filter-out $@,$(MAKECMDGOALS))
