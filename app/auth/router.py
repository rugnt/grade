from fastapi import APIRouter, Depends, Body
from app.auth.schemas import Registration
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from typing import Annotated
from app.auth.services import registration_user
from app.auth.services import refresh as refresh_token
from app.auth.services import login_user, logout_user


router = APIRouter(prefix='/auth')


@router.post('/registration')
async def registration(
    db: Annotated[AsyncSession, Depends(get_db)],
    registration: Registration
):
    return await registration_user(db, registration.email, registration.password1)


@router.post('/refresh')
async def refresh(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Body()],
):
    return await refresh_token(db, token)


@router.post('/login')
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    email: Annotated[str, Body()],
    password: Annotated[str, Body()]
):
    return await login_user(db, email, password)


@router.post('/logout')
async def logout(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Body()],
):
    return await logout_user(db, token)