import tiktoken
from sentence_transformers import SentenceTransformer

encoding = tiktoken.encoding_for_model("gpt-5-nano")

embedder = SentenceTransformer("BAAI/bge-m3")

def length_function(text: str) -> int:
    encoded = encoding.encode(text)
    return encoded, len(encoded)