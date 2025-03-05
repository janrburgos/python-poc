.PHONY: build
build:
	docker build --rm -t fastapi-local-app -f Dockerfile .
	docker image prune -f

.PHONY: update
update:
	docker run --rm -v $(PWD):/app fastapi-local-app pipenv lock

.PHONY: dotEnvLocal
dotEnvLocal:
	cp .env-local .env

.PHONY: start
start:
	docker run --rm --name fastapi-app -p 8000:8000 fastapi-local-app


.PHONY: shell
shell:
	docker exec -it fastapi-app bash
