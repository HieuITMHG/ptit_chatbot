from fastapi import Depends, HTTPException,  Request, WebSocket, status
from typing import Annotated
import jwt
from core.config import settings
from app.schemas.user import User
from app.repositories.user_repo import get_user

async def get_current_user(
    request: Request = None, 
    websocket: WebSocket = None,
):
    token = None

    if request:
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

    elif websocket:
        token = websocket.query_params.get("token")

    if not token:
        if websocket:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if not username:
            raise jwt.PyJWTError()
            
        user_data = get_user(username) 
        if not user_data:
            raise jwt.PyJWTError()
            
        return User(**user_data)

    except jwt.PyJWTError:
        if websocket:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        raise HTTPException(status_code=401, detail="Token expired or invalid")


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user