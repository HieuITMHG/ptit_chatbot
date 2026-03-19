from core.qdrant import client
from qdrant_client.models import Prefetch, FusionQuery, Fusion, SparseVector
from FlagEmbedding import BGEM3FlagModel
from openai import OpenAI
from core.config import settings
from pipelines.reranking.cross_encoder_rerank import cross_encoder_reranker
import time

openai_client = OpenAI(api_key=settings.openai_key)

class BGEHybirdRag:
    def __init__(self, embedding_model, collection_name):
        self.embedding_model = BGEM3FlagModel(embedding_model, use_fp16=True)
        self.collection_name = collection_name
        
    def retrieve(self, query: str, top_k: int, search_limit: int = 50):
        start_search = time.perf_counter()
        
        encoded = self.embedding_model.encode(query, return_dense=True, return_sparse=True)
        query_dense = encoded["dense_vecs"]
        sparse_out = encoded["lexical_weights"]
        
        sparse_indices = [int(k) for k in sparse_out.keys()]
        sparse_values = list(sparse_out.values())

        for attempt in range(5):
            try:
                contexts = client.query_points(
                    collection_name=self.collection_name,
                    prefetch=[
                        Prefetch(
                            query=query_dense.tolist(),
                            using="dense",
                            limit=search_limit,
                        ),
                        Prefetch(
                            query=SparseVector(indices=sparse_indices, values=sparse_values),
                            using="sparse",
                            limit=search_limit,
                        ),
                    ],
                    query=FusionQuery(fusion=Fusion.RRF),
                    with_payload=True,
                    limit=10 
                )
                break
            except Exception as e:
                print(f"Retry Qdrant: {e}")
                time.sleep(2)

        end_search = time.perf_counter()
        print(f"Hybrid search latency (Qdrant RRF): {end_search - start_search:.4f}s")

        results = []

        if hasattr(contexts, 'points'): 
            for point in contexts.points:
                payload = point.payload
                results.append({
                    "id": point.id.replace("-", ""),
                    "doc_url": payload["document_url"],
                    "chunk_index": payload["chunk_index"],
                    "token_count": payload["token_count"],
                    "title": payload["title"],
                    "chunk_content": payload["chunk_content"],
                    "author": payload.get("author", ""),
                    "published_date": payload.get("published_date", ""),
                    "score": point.score,
                })

        start_rerank = time.perf_counter()
        if results: #
            results = cross_encoder_reranker(
                unordered_contexts=results,
                query=query
            )
        end_rerank = time.perf_counter()
        print(f"Rerank latency: {end_rerank - start_rerank:.4f}s")

        return results[:top_k]
    
    def generate(self, query, contexts):
        prompt_template = """
            Bạn là trợ lý ảo hỗ trợ trả lời câu hỏi cho sinh viên và thành viên của 
            Học viện Công nghệ Bưu chính Viễn thông (PTIT) cơ sở TP.HCM.

            Hãy dùng thông tin trong các dữ liệu được cung cấp để trả lời câu hỏi.

            Quy tắc:
            - Chỉ trả lời dựa trên thông tin có trong dữ liệu.
            - Không nhắc đến từ “context”, “dữ liệu được cung cấp”, hay giải thích cách bạn tìm thông tin.
            - Trả lời ngắn gọn, tự nhiên, dễ hiểu như khi giải thích cho sinh viên.
            - Nếu dữ liệu không có thông tin để trả lời câu hỏi, hãy nói đơn giản: "Hiện chưa có thông tin về nội dung này."
            - Cuối câu trả lời hãy liệt kê các nguồn tham khảo (URL).

            Dữ liệu:
            {contexts_str}

            Câu hỏi: {query}
        """

        contexts_list = []
        for i, ctx in enumerate(contexts):
            context_text = f'--- Nội dung {i+1} ---\n{ctx["chunk_content"]}\nNguồn: {ctx["doc_url"]}'
            contexts_list.append(context_text)
            print(f"Nguồn {i+1}: {ctx['doc_url']}")

        contexts_str = "\n\n".join(contexts_list)

        prompt = prompt_template.format(
            contexts_str=contexts_str,
            query=query
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2 
        )

        return response.choices[0].message.content

if __name__ == "__main__":
    rag_engine = BGEHybirdRag(embedding_model="BAAI/bge-m3",
                              collection_name="semantic_collecction")
    
    query = "Đại hội Đảng bộ Học viện Công nghệ Bưu chính Viễn thông lần thứ VII tổ chức trong khoảng thời gian nào và đề ra những mục tiêu gì cho nhiệm kỳ 2025-2030?"

    start_time = time.perf_counter()
    
    results = rag_engine.retrieve(query=query, top_k=3) 

    end_time = time.perf_counter()

    latency = end_time - start_time

    print("\n=== TOP KẾT QUẢ ĐÃ ĐƯỢC BGE RERANK ===")
    for r in results:
        print(f"ID: {r['id']} | URL: {r['doc_url']}")

    print(f"Total Retrieval Latency: {latency:.4f}s\n")
    # print("--- Câu trả lời từ LLM ---")
    # print(rag_engine.generate(query=query, contexts=results))