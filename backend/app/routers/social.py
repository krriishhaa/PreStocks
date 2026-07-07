from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.services.social_service import SocialService
from app.core.security import get_current_user_id

router = APIRouter()


class PostCreate(BaseModel):
    ticker: str = Field(max_length=10)
    reasoning: str = Field(max_length=300)
    action: str = Field(default="", max_length=10)


class CommentCreate(BaseModel):
    content: str = Field(max_length=500)


@router.get("/feed")
async def get_feed(
    filter: str = Query(default="all", pattern="^(all|following|network)$"),
    sort: str = Query(default="recent", pattern="^(recent|insightful|engagement)$"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = SocialService(db)
    return await service.get_feed(user_id, filter, sort, offset, limit)


@router.post("/posts")
async def create_post(
    data: PostCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = SocialService(db)
    return await service.create_post(user_id, data)


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = SocialService(db)
    return await service.toggle_like(user_id, post_id)


@router.get("/posts/{post_id}/comments")
async def get_comments(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    service = SocialService(db)
    return await service.get_comments(post_id)


@router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: str,
    data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = SocialService(db)
    return await service.add_comment(user_id, post_id, data.content)
