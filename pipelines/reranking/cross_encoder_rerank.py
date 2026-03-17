# from FlagEmbedding import FlagReranker

# model = FlagReranker(
#     "BAAI/bge-reranker-base",
#     use_fp16=False,
#     devices=["cpu"]
# )

# def cross_encoder_reranker(unordered_contexts: list, query: str) -> list:
#     pairs = [[query, context["chunk_content"]] for context in unordered_contexts]

#     scores = model.compute_score(pairs)

#     scored_contexts = [
#         {**context, "score": score}
#         for context, score in zip(unordered_contexts, scores)
#     ]

#     ranked_contexts = sorted(
#         scored_contexts,
#         key=lambda x: x["score"],
#         reverse=True
#     )

#     return ranked_contexts

from flashrank import Ranker, RerankRequest
import time

# Khởi tạo mô hình FlashRank (đã được nén và tối ưu ONNX)
# ms-marco-MultiBERT-L-12 là mô hình đa ngôn ngữ, hỗ trợ tiếng Việt rất tốt và cực kỳ nhẹ
print("Đang tải mô hình Rerank ONNX...")
ranker = Ranker(model_name="ms-marco-MultiBERT-L-12", cache_dir="./models") 

def cross_encoder_reranker(unordered_contexts: list, query: str) -> list:
    """
    Hàm này nhận vào list các context và trả về list đã sắp xếp, 
    giống hệt output của hàm cũ để code của bạn không bị lỗi.
    """
    start_time = time.perf_counter()

    # 1. Chuyển đổi format list của bạn sang format mà FlashRank hiểu
    passages = []
    for i, context in enumerate(unordered_contexts):
        passages.append({
            "id": str(i),                         # Tạo 1 ID tạm thời
            "text": context["chunk_content"],     # Nội dung để đem đi so sánh
            "meta": context                       # Nhét toàn bộ object cũ vào đây để lát lấy ra
        })

    # 2. Đóng gói thành RerankRequest
    req = RerankRequest(query=query, passages=passages)

    # 3. Chạy Rerank siêu tốc
    flashrank_results = ranker.rerank(req)

    # 4. Bóc tách dữ liệu trả về đúng format cũ của bạn (kèm theo 'score')
    ranked_contexts = []
    for res in flashrank_results:
        original_context = res["meta"]             # Lấy lại cái object gốc của bạn
        original_context["score"] = res["score"]   # Cập nhật điểm số mới do FlashRank chấm
        ranked_contexts.append(original_context)

    end_time = time.perf_counter()
    print(f"Thời gian Rerank (ONNX): {end_time - start_time:.4f} giây")

    return ranked_contexts