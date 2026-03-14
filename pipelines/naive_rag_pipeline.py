from core.qdrant import client
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from core.config import settings

openai_client = OpenAI(api_key=settings.openai_key)

class NaiveRag:
    def __init__(self, embedding_model, collection_name):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.collection_name = collection_name

    def retriever(self, query: str): 
        contexts = client.query_points(collection_name=self.collection_name,
                                       query=self.embedding_model.encode(query),
                                       with_payload=True,
                                       limit=10)
        result =  []
        for point in contexts.points:
            payload = point.payload
            result.append({
                "doc_url": payload["document_url"],
                "chunk_index": payload["chunk_index"],
                "token_count": payload["token_count"],
                "title": payload["title"],
                "chunk_content": payload["chunk_content"],
                "author": payload["author"],
                "published_date": payload["published_date"]
            })

        return result
    
    def generator(self, query, contexts):
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
            {context_1}
            {context_2}
            {context_3}
            {context_4}
            {context_5}

            Câu hỏi: {query}
        """

        prompt = prompt_template.format(
            context_1 = contexts[0]["chunk_content"],
            context_2 = contexts[1]["chunk_content"],
            context_3 = contexts[2]["chunk_content"],
            context_4 = contexts[3]["chunk_content"],
            context_5 = contexts[4]["chunk_content"],
            query = query
        )

        response = openai_client.responses.create(
            model="gpt-5-nano",
            input=prompt,
        )

        return response.output_text




if __name__ == "__main__":
    rag_engine = NaiveRag(embedding_model="BAAI/bge-m3",
                          collection_name="main_collection")
    
    query = "Hãy tổng hợp cho tôi các hoạt động của đoàn trường năm 2025"
    
    results = rag_engine.retriever(query=query)

    res = rag_engine.generator(query=query, contexts=results)

    print(res)