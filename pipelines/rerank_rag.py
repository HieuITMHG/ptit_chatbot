from core.qdrant import client
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from core.config import settings
from pipelines.reranking.cross_encoder_rerank import cross_encoder_reranker
import time

openai_client = OpenAI(api_key=settings.openai_key)

class RerankRag:
    def __init__(self, embedding_model, collection_name):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.collection_name = collection_name

    def retrieve(self, query: str, top_k: int): 
        for attempt in range(3):
            try:
                contexts = client.query_points(collection_name=self.collection_name,
                                                query=self.embedding_model.encode(query),
                                                with_payload=True,
                                                limit=20)
                break
            except Exception as e:
                print(f"Retry: {e}")
                time.sleep(2)

        results =  []
        for point in contexts.points:
            payload = point.payload
            results.append({
                "id": point.id.replace("-", ""),
                "doc_url": payload["document_url"],
                "chunk_index": payload["chunk_index"],
                "token_count": payload["token_count"],
                "title": payload["title"],
                "chunk_content": payload["chunk_content"],
                "author": payload["author"],
                "published_date": payload["published_date"]
            })
        
        reranked_contexts = cross_encoder_reranker(unordered_contexts=results[: 10],
                                                   query=query)

        return reranked_contexts[0: top_k]
    
    def generate(self, query, contexts):
        prompt_template = """
            Bạn là trợ lý ảo hỗ trợ trả lời câu hỏi cho sinh viên và thành viên của 
            Học viện Công nghệ Bưu chính Viễn thông (PTIT) cơ sở TP.HCM.

            Hãy dùng thông tin trong các dữ liệu được cung cấp để trả lời câu hỏi.

            Quy tắc:
            - Chỉ trả lời dựa trên thông tin có trong dữ liệu.
            - Không nhắc đến từ “context”, “dữ liệu được cung cấp”, hay giải thích cách bạn tìm thông tin.
            - Trả lời ngắn gọn, tự nhiên, dễ hiểu như khi giải thích cho sinh viên.
            - Nếu dữ liệu không có thông tin để trả lời câu hỏi, hãy nói đơn giản:
            "Hiện chưa có thông tin về nội dung này."
            - Cuối câu trả lời hãy liệt kê các nguồn tham khảo (URL).

            Dữ liệu:
            {context_1}
            {context_2}
            {context_3}

            Câu hỏi: {query}
        """

        context_1 = f'{contexts[0]["chunk_content"]}\nNguồn: {contexts[0]["doc_url"]}'
        context_2 = f'{contexts[1]["chunk_content"]}\nNguồn: {contexts[1]["doc_url"]}'
        context_3 = f'{contexts[2]["chunk_content"]}\nNguồn: {contexts[2]["doc_url"]}'

        print(contexts[0]["doc_url"])
        print(contexts[1]["doc_url"])
        print(contexts[2]["doc_url"])

        prompt = prompt_template.format(
            context_1 = context_1,
            context_2 = context_2,
            context_3 = context_3,
            query = query
        )

        response = openai_client.responses.create(
            model="gpt-5-nano",
            input=prompt,
        )

        return response.output_text

if __name__ == "__main__":
    rag_engine = RerankRag(embedding_model="BAAI/bge-m3",
                          collection_name="enrich_hybrid_collection")
    
    query = "tổng hợp hoạt động đoàn"
    
    results = rag_engine.retrieve(query=query, top_k=5)

    for r in results:
        print(r["id"])

    print(rag_engine.generate(query=query, contexts=results))




    