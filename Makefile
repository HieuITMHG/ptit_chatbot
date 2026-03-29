etl-rerank:
	@python3 -m run ingest --crawl --parse --chunk --embed --rag rerank

crawl:
	@python3 -m run ingest --crawl

validate-retrieval:
	@python3 -m run validate --retrieval --rag 

build-dev:
	@docker compose -f docker-compose.dev.yml --build

run-dev:
	@docker compose -f docker-compose.dev.yml up -d

stop-dev:
	@docker compose -f docker-compose.dev.yml down

build-prod:
	@docker compose -f docker-compose.prod.yml --build

run:
	@docker compose -f docker-compose.prod.yml up -d

stop:
	@docker compose -f docker-compose.prod.yml down

etl-dev:
	@docker compose -f docker-compose.dev.yml up -d
	@docker compose -f docker-compose.dev.yml run --rm etl


