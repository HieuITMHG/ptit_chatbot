#!/bin/sh

echo "Running ETL pipeline..."

python3 -m run ingest --crawl --parse --chunk --embed --rag rerank

echo "ETL done, starting API..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000