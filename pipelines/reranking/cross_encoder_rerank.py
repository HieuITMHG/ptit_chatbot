from FlagEmbedding import FlagReranker

model = FlagReranker(
    "BAAI/bge-reranker-base",
    use_fp16=False,
    devices=["cpu"]
)

def cross_encoder_reranker(unordered_contexts: list, query: str) -> list:
    pairs = [[query, context["chunk_content"]] for context in unordered_contexts]

    scores = model.compute_score(pairs)

    scored_contexts = [
        {**context, "score": score}
        for context, score in zip(unordered_contexts, scores)
    ]

    ranked_contexts = sorted(
        scored_contexts,
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked_contexts