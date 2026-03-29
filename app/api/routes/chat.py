from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import jwt
from core.config import settings
from app.repositories.user_repo import get_user
from app.schemas.user import User
from app.tasks.chat_task import get_answer
from app.services.chat_service import listen_to_redis

router = APIRouter(tags=["chat"])

async def authenticate_websocket(websocket: WebSocket) -> User | None:
    token = websocket.query_params.get("token")
    
    if not token:
        token = websocket.cookies.get("access_token")

    if not token:
        print("Xác thực thất bại: Không có token")
        await websocket.close(code=1008) 
        return None

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if not username:
            await websocket.close(code=1008)
            return None
            
    except jwt.PyJWTError:
        print("Xác thực thất bại: Token hết hạn hoặc không hợp lệ")
        await websocket.close(code=1008)
        return None

    user = get_user(username)
    if not user:
        await websocket.close(code=1008)
        return None

    return User(**user)


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    current_user = await authenticate_websocket(websocket)
    if not current_user:
        return  
    
    print(f"User {current_user.username} đã kết nối WebSocket thành công")

    try:
        while True:
            data = await websocket.receive_json()
            prompt = data.get("prompt")

            if not prompt:
                await websocket.send_json({
                    "status": "Error",
                    "message": "Prompt is required"
                })
                continue

            task_id = f"task_{current_user.username}_{int(asyncio.get_event_loop().time())}"

            get_answer.delay(task_id, prompt, current_user.username)

            await websocket.send_json({
                "status": "Processing",
                "task_id": task_id,
                "message": "AI đang suy nghĩ..."
            })

            asyncio.create_task(
                listen_to_redis(task_id, websocket)
            )

    except WebSocketDisconnect:
        print(f"Client {current_user.username} đã chủ động ngắt kết nối.")
        
    except Exception as e:
        print(f"Lỗi WebSocket không xác định: {e}")
        try:
            await websocket.close()
        except RuntimeError:
            pass