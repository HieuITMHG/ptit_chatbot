from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from model.chat_request import ChatRequest
from model.chat_response import ChatResponse
from core.config_loader import PipelineConfig

from pipelines.rerank_rag import RerankRag, get_answer
from FlagEmbedding import BGEM3FlagModel

config = PipelineConfig("configs/rerank_rag.yaml")

embedder = BGEM3FlagModel(config.embedding["model"])
rag_engine = RerankRag(
    embedding_model=embedder,
    collection_name=config.embedding["vector_col_name"]
)

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest, 
):
    if len(req.request_content) < 3:
        return ChatResponse(
            response_content="Request too short",
            sources=[],
            metadata={
                "timestamp": datetime.now(timezone.utc),
            }
        )

    try:
        result = get_answer(rag_engine=rag_engine, 
                            prompt= req.request_content,
                            top_k=5)

        return ChatResponse(
            response_content=result["text_res"],
            sources=result["ref_source"],
            metadata={
                "timestamp": datetime.now(timezone.utc),
            }
        )

    except Exception as e:
        return HTTPException(status_code=400, detail=e)