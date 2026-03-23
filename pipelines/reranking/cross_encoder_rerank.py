from flashrank import Ranker, RerankRequest
import time
import os

current_file_dir = os.path.dirname(os.path.abspath(__file__))

base_project_dir = os.path.abspath(os.path.join(current_file_dir, "../../"))
model_cache_path = os.path.join(base_project_dir, "models")

if not os.path.exists(model_cache_path):
    os.makedirs(model_cache_path)

print(f"Đang kiểm tra mô hình Rerank tại: {model_cache_path}")

try:
    ranker = Ranker(model_name="ms-marco-MultiBERT-L-12", cache_dir=model_cache_path) 
except Exception as e:
    print(f"Lỗi khởi tạo Ranker: {e}")
    print("Mẹo: Nếu server không có internet, hãy dùng 'scp' copy thư mục model từ local lên.")
    raise

def cross_encoder_reranker(unordered_contexts: list, query: str) -> list:
    """
    Hàm này nhận vào list các context và trả về list đã sắp xếp, 
    giống hệt output của hàm cũ để code của bạn không bị lỗi.
    """
    start_time = time.perf_counter()

    passages = []
    for i, context in enumerate(unordered_contexts):
        passages.append({
            "id": str(i),                         
            "text": context["chunk_content"],    
            "meta": context                      
        })

    req = RerankRequest(query=query, passages=passages)

    flashrank_results = ranker.rerank(req)

    ranked_contexts = []
    for res in flashrank_results:
        original_context = res["meta"]           
        original_context["score"] = res["score"]  
        ranked_contexts.append(original_context)

    end_time = time.perf_counter()
    print(f"Thời gian Rerank (ONNX): {end_time - start_time:.4f} giây")

    return ranked_contexts