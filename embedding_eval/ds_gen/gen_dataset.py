from openai import OpenAI
from rapidfuzz import fuzz
import json

from core.database import db
from core.config import settings

from model.query import Query
from model.quote import Quote
from model.quote_query import QuoteQuery

documents_collection = db["documents"]
queries_collection = db["queries"]
quoties_collection = db["quoties"]
quote_query_collection = db["quote_query"]

client = OpenAI(api_key=settings.openai_key)

request_template = """
Bạn đang tạo dataset để đánh giá hệ thống truy hồi thông tin (retrieval / embedding).

Từ đoạn văn bản dưới đây, hãy tạo ra 3 câu hỏi mà người dùng có thể tìm kiếm để tìm được thông tin trong văn bản.

CHÚ Ý QUAN TRỌNG: Chỉ trả về duy nhất mảng JSON. Tuyệt đối không giải thích, không chào hỏi, không dùng markdown block (```json).

Yêu cầu:
- Câu hỏi phải tự nhiên như truy vấn tìm kiếm của người dùng
- Có thể paraphrase nội dung trong văn bản
- Không copy nguyên câu trong văn bản
- Mỗi câu hỏi có thể liên quan đến một hoặc nhiều đoạn trong văn bản

Với mỗi câu hỏi, hãy trả về các đoạn quote từ văn bản có thể dùng để trả lời câu hỏi đó.

Quote phải:
- được copy chính xác từ văn bản
- có thể dài nhiều câu
- có thể có nhiều quote cho một câu hỏi

Trả về kết quả theo format JSON:

[
  {{
    "query": "...",
    "quotes": [
      "...",
      "..."
    ]
  }},
  {{
    "query": "...",
    "quotes": [
      "..."
    ]
  }},
  {{
    "query": "...",
    "quotes": [
      "...",
      "..."
    ]
  }}
]

Đây là văn bản:

{context}
"""

def get_max_id(db, collection_name: str) -> int:

    last_doc = db[collection_name].find_one({}, sort=[("id", -1)])
    
    if last_doc and "id" in last_doc:
        return last_doc["id"]
    
    return 0

def get_best_quote(context: str, quote: str):

    alignment = fuzz.partial_ratio_alignment(quote, context)

    score = alignment.score
    start = alignment.dest_start
    end = alignment.dest_end

    best_span = context[start:end]

    return best_span, score

def gen_dataset():
    docs = documents_collection.find({})
    query_count = get_max_id(db=db,collection_name="queries")
    quote_count = get_max_id(db=db, collection_name="quoties")
    
    for doc in docs:
        if quoties_collection.count_documents({"doc_url": doc["source_url"]}, limit=1) > 0:
            continue
        context = doc["content"][: 2000]

        prompt = request_template.format(context=context)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        try:
            data = json.loads(response.output_text)
        except Exception as e:
            with open("embedding_eval/ds_gen/logs.txt", "w", encoding="utf-8") as f:
                f.write(f"{e}  + \n\n + {response.output_text}")

        for que in data:
            query = Query(id = query_count, query_content=que["query"])

            for quo in que["quotes"]:
                true_quote, score = get_best_quote(context=context, quote=quo)
                quote = Quote(id=quote_count, quote_content=true_quote, doc_url=doc["source_url"])
                quotequery = QuoteQuery(query_id=query.id, quote_id=quote.id)

                try:
                    quoties_collection.insert_one(quote.model_dump())
                    quote_query_collection.insert_one(quotequery.model_dump())
                except Exception as e:
                    print(e)

                quote_count += 1
            
            try:
                queries_collection.insert_one(query.model_dump())
            except Exception as e:
                print(e)

            query_count +=1

if __name__ == "__main__":
    gen_dataset()