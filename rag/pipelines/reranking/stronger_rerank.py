import os
import time
import torch
from sentence_transformers import CrossEncoder

current_file_dir = os.path.dirname(os.path.abspath(__file__))
base_project_dir = os.path.abspath(os.path.join(current_file_dir, "../../"))
model_cache_path = os.path.join(base_project_dir, "models")

MODEL_NAME = "BAAI/bge-reranker-large"

device = "cuda"
print(f"--- Đang chạy Rerank trên thiết bị: {device} ---")

try:
    ranker = CrossEncoder(MODEL_NAME, cache_folder=model_cache_path, device=device)
    print(f"--- Khởi tạo Ranker thành công: {MODEL_NAME} ---")
except Exception as e:
    print(f"Lỗi khởi tạo Ranker: {e}")
    raise

def cross_encoder_reranker(unordered_contexts: list, query: str) -> list:
    if not unordered_contexts:
        return []

    start_time = time.perf_counter()

    pairs = [[query, context.get("chunk_content", "")] for context in unordered_contexts]
    
    scores = ranker.predict(pairs)

    ranked_contexts = []
    for i, context in enumerate(unordered_contexts):
        context["score"] = float(scores[i])
        ranked_contexts.append(context)

    ranked_contexts.sort(key=lambda x: x["score"], reverse=True)

    end_time = time.perf_counter()
    print(f"Rerank hoàn tất: {len(ranked_contexts)} docs | Thời gian: {end_time - start_time:.4f} giây")

    return ranked_contexts