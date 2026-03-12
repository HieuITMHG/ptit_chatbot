from openai import OpenAI
from core.database import db
from core.config import settings
import json

documents_collection = db["documents"]

client = OpenAI(api_key=settings.openai_key)

url = "/thong-tin-nganh-dao-tao/gioi-thieu-nganh-cong-nghe-phan-mem.html"

context = ""

request_template = """
Bạn đang tạo dataset để đánh giá hệ thống truy hồi thông tin (retrieval / embedding).

Từ đoạn văn bản dưới đây, hãy tạo ra 3 câu hỏi mà người dùng có thể tìm kiếm để tìm được thông tin trong văn bản.

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

if __name__ == "__main__":
    doc = documents_collection.find_one({"source_url": url})

    context = doc["content"]

    prompt = request_template.format(context=context[:2000])

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    data = json.loads(response.output_text)

    with open("embedding_eval/ds_gen/test_output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(response)