from core.qdrant import client
from FlagEmbedding import BGEM3FlagModel
from openai import OpenAI
from core.config import settings
from pipelines.reranking.cross_encoder_rerank import cross_encoder_reranker
import time

openai_client = OpenAI(api_key=settings.openai_key)

class RerankRag:
    def __init__(self, embedding_model, collection_name):
        self.embedding_model = BGEM3FlagModel(embedding_model, use_fp16=True)
        self.collection_name = collection_name

    def retrieve(self, query: str, top_k: int): 
        encoded_output = self.embedding_model.encode(query, return_dense=True, return_sparse=False, return_colbert_vecs=False)
        query_dense = encoded_output["dense_vecs"].tolist()

        for attempt in range(3):
            try:
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
    
def get_answer(rag_engine, prompt, top_k = 5):
    contexts = rag_engine.retrieve(query=prompt, top_k=top_k)
    source_urls = [f"https://ptithcm.edu.vn{context['doc_url']}" for context in contexts]
    return {
        "text_res": rag_engine.generate(query=prompt, contexts=contexts),
        "ref_source": source_urls
    }
        