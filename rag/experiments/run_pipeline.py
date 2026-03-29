from core.config import settings
from core.qdrant import client
from data_ingestion.chunking.helpers import embedder
from openai import OpenAI

openai_client = OpenAI(api_key=settings.openai_key)

prompt_template = """
Bạn là trợ lý AI của PTIT.

Context:
{context}

Question:
{question}

Hãy trả lời dựa trên context trên.
"""

if __name__ == "__main__":
    request = input("Nhập prompt: ")

    contexts = client.query_points(
        collection_name="main_collection",
        query = embedder.encode(request),
        with_payload=True,
        limit=5
    )

    prompt = prompt_template.format(
        context=contexts.points[0].payload["chunk_content"],
        question=request
    )

    response = openai_client.responses.create(
            model="gpt-5-nano",
            input=prompt,
        )

    print(response.output_text)