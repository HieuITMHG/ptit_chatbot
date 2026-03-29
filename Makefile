elt-rerank:
	@python -m run ingest --crawl --parse --chunk --embed --rag rerank

crawl:
	@python -m run ingest --crawl

validate-retrieval:
	@python -m run validate --retrieval --rag 

dev:
	@docker compose -f docker-compose.dev.yml up --build

run-dev:
	@docker compose -f docker-compose.dev.yml up -d

stop-dev:
	@docker compose -f docker-compose.dev.yml down

prod:
	@docker compose -f docker-compose.prod.yml up --build

run:
	@docker compose -f docker-compose.prod.yml up -d

stop:
	@docker compose -f docker-compose.prod.yml down


