from core.qdrant import client
from FlagEmbedding import BGEM3FlagModel
from openai import OpenAI
from core.config import settings
from pipelines.reranking.cross_encoder_rerank import cross_encoder_reranker
import time

openai_client = OpenAI(api_key=settings.openai_key)

class RerankRag:
    def __init__(self, embedding_model, collection_name):
        # 1. Thay thế SentenceTransformer bằng BGEM3FlagModel
        self.embedding_model = BGEM3FlagModel(embedding_model, use_fp16=True)
        self.collection_name = collection_name

    def retrieve(self, query: str, top_k: int): 
        # 2. Mã hóa câu hỏi và CHỈ lấy dense_vecs
        encoded_output = self.embedding_model.encode(query, return_dense=True, return_sparse=False, return_colbert_vecs=False)
        query_dense = encoded_output["dense_vecs"].tolist()

        for attempt in range(3):
            try:
                # 3. Search Qdrant thuần bằng Dense Vector
                contexts = client.query_points(
                    collection_name=self.collection_name,
                    query=query_dense, 
                    with_payload=True,
                    using="dense",
                    limit=20
                )
                break
            except Exception as e:
                print(f"Retry: {e}")
                time.sleep(2)

        results = []
        if hasattr(contexts, 'points'):
            for point in contexts.points:
                payload = point.payload
                results.append({
                    "id": point.id.replace("-", ""),
                    "doc_url": payload.get("document_url", ""),
                    "chunk_index": payload.get("chunk_index", 0),
                    "token_count": payload.get("token_count", 0),
                    "title": payload.get("title", ""),
                    "chunk_content": payload.get("chunk_content", ""),
                    "author": payload.get("author", ""),
                    "published_date": payload.get("published_date", "")
                })
        
        # 4. Đưa top 10 kết quả vào Re-ranker
        reranked_contexts = cross_encoder_reranker(
            unordered_contexts=results[:10],
            query=query
        )

        return reranked_contexts[:top_k]
    
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
            {contexts_str}

            Câu hỏi: {query}
        """

        # Tránh lỗi IndexError bằng cách duyệt động qua mảng contexts
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

        # Cú pháp OpenAI Chat Completions mới
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", # Đổi lại model hợp lệ nhé (gpt-4o-mini hoặc gpt-3.5-turbo)
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

if __name__ == "__main__":
    rag_engine = RerankRag(embedding_model="BAAI/bge-m3",
                          collection_name="semantic_collecction") # Đã sửa lỗi typo collecction
    
    query = "NCKH năm 2024"
    
    # Lấy top 5 kết quả tốt nhất
    results = rag_engine.retrieve(query=query, top_k=5)

    print("\n=== TOP KẾT QUẢ ĐÃ ĐƯỢC RERANK ===")
    for r in results:
        print(f"ID: {r['id']} | URL: {r['doc_url']}")

    print("\n=== TRẢ LỜI TỪ LLM ===")
    print(rag_engine.generate(query=query, contexts=results))