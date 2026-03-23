from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from celery.exceptions import TimeoutError
from model.chat_request import ChatRequest
from model.chat_response import ChatResponse

from .tasks import chat_rag_task

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
    task = chat_rag_task.delay(req.request_content)

    try:
        result = task.get(timeout=60)

        return ChatResponse(
            response_content=result["text_res"],
            sources=result["ref_source"],
            metadata={
                "timestamp": datetime.now(timezone.utc),
            }
        )

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="RAG processing timeout, please try again later"
        )