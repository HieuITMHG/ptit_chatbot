from core.qdrant import client
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from core.config import settings
from pipelines.reranking.cross_encoder_rerank import cross_encoder_reranker
import time
from .bm25 import BM25
from .bm25_search import search, raw_docs, bm25
import time

openai_client = OpenAI(api_key=settings.openai_key)

class HybirdRag:
    def __init__(self, embedding_model, collection_name):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.collection_name = collection_name

    def dense_retrieve(self, query: str, limit: int = 50): 
        for attempt in range(5):
            try:
                contexts = local_client.query_points(collection_name=self.collection_name,
                                                query=self.embedding_model.encode(query),
                                                with_payload=True,
                                                limit=limit)
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
                "published_date": payload["published_date"],
                "score": point.score,
            })
        
        return results
    
    def reciprocal_rank_fusion(self, dense_results, sparse_results, k=60):

        rrf_scores = {}
        doc_lookup = {}

        for rank, doc in enumerate(dense_results):
            doc_id = doc["id"]

            score = 1 / (k + rank + 1)

            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + score
            doc_lookup[doc_id] = doc

        for rank, doc in enumerate(sparse_results):
            doc_id = doc["id"]

            score = 1 / (k + rank + 1)

            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + score

            if doc_id not in doc_lookup:
                doc_lookup[doc_id] = doc

        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        results = [doc_lookup[doc_id] for doc_id, _ in ranked]

        return results
        
    def retrieve(self, query: str, top_k:int, search_limit:int = 50):
        start_dense = time.perf_counter()
        dense_results = self.dense_retrieve(
            query=query,
            limit=search_limit
        )
        end_dense = time.perf_counter()
        dense_time = end_dense - start_dense
        print(f"Dense search latency: {dense_time}")

        sparse_results = search(
            query=query,
            bm25=bm25,
            raw_docs=raw_docs,
            limit=search_limit
        )

        fused_results = self.reciprocal_rank_fusion(
            dense_results,
            sparse_results
        )

        fused_results = fused_results[0: 10]

        start_rerank = time.perf_counter()
        fused_results = cross_encoder_reranker(
            unordered_contexts=fused_results,
            query=query
        )
        end_rerank = time.perf_counter()
        rerank_time = end_rerank - start_rerank
        print(f"Rerank latency: {rerank_time}")

        return fused_results[:top_k]
    
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
    rag_engine = HybirdRag(embedding_model="BAAI/bge-m3",
                          collection_name="enrich_hybrid_collection")
    
    query = "tư vấn tuyển sinh đại học cao đẳng ptit 2014 2025"

    start_time = time.perf_counter()
    
    results = rag_engine.retrieve(query=query, top_k=5)

    end_time = time.perf_counter()

    latency = end_time - start_time

    for r in results:
        print(r["id"])

    print(f"Latency: {latency}")

    # print(rag_engine.generate(query=query, contexts=results))




    