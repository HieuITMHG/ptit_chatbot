from fastapi import APIRouter, Depends, Response, Request
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
import jwt

from app.schemas.user import User
from app.services.auth_service import authenticate_user,create_access_token, create_refresh_token
from ..deps import get_current_active_user
from core.config import settings

router = APIRouter(tags=["auth"])

@router.post("/login/")
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=7 * 24 * 3600,
        path="/"
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.post("/refresh/")
async def refresh_access_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})

    response.set_cookie(key="access_token", value=new_access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True)

    return {
        "access_token": new_access_token, 
        "token_type": "bearer"
    }

@router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    return current_user

@router.post("/logout/")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    
    return {"detail": "Successfully logged out"}