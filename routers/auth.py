from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from jose import JWTError, jwt
from config import settings
from pydantic import BaseModel

from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_password_hash
)
from core.dependencies import get_current_user
from database import get_session, User

router = APIRouter(tags=["authentication"])

class UserCreate(BaseModel):
    username: str
    password: str

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    # Authentication logic
    result = await session.exec(
        select(User).where(User.username == form_data.username)
    )
    user = result.first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    # Registration logic
    existing_user = await session.exec(
        select(User).where(User.username == user_data.username)
    )
    if existing_user.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = User(username=user_data.username, hashed_password=hashed_password)
    
    session.add(user)
    await session.commit()
    
    return {"message": "User created successfully"}

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_token(token_data: TokenRefreshRequest):
    try:
        # Decode the refresh token from the request body
        payload = jwt.decode(token_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")

        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")
