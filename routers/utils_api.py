from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from config import settings
from db.operations import get_db
from models.users import User
from schemas.responses_schema import Token
from utils.security import create_access_token

router = APIRouter(
    prefix="/utils",
    tags=["Utils"]
)


@router.post("/token", response_model=Token)
async def get_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.username == form_data.username)
    user = (await db.scalars(query)).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
