from openai import OpenAI
import base64
from core.config import settings

client = OpenAI(api_key=settings.openai_key)

# đọc ảnh và encode base64
with open("embedding_eval/vll.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hãy phân tích nội dung của bức ảnh này"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)

print(response)