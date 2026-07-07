from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.social import SocialPost, SocialComment, SocialLike
from app.models.user import User


class SocialService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_feed(self, user_id: int, filter_type: str, sort: str, offset: int, limit: int) -> list[dict]:
        query = select(SocialPost).options(selectinload(SocialPost.user))

        if sort == "recent":
            query = query.order_by(SocialPost.created_at.desc())
        elif sort == "insightful":
            query = query.order_by(SocialPost.engagement_count.desc())
        else:
            query = query.order_by(SocialPost.engagement_count.desc())

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        posts = result.scalars().all()

        # Check likes
        like_result = await self.db.execute(
            select(SocialLike.post_id).where(SocialLike.user_id == user_id)
        )
        liked_ids = {row[0] for row in like_result.all()}

        return [self._post_to_dict(p, p.id in liked_ids) for p in posts]

    async def create_post(self, user_id: int, data) -> dict:
        post = SocialPost(
            user_id=user_id,
            content=data.reasoning if hasattr(data, "reasoning") else data.content,
            tickers=[data.ticker.upper()] if hasattr(data, "ticker") else [],
            trade_type=data.action if hasattr(data, "action") else None,
        )
        self.db.add(post)
        await self.db.flush()

        result = await self.db.execute(
            select(SocialPost).options(selectinload(SocialPost.user)).where(SocialPost.id == post.id)
        )
        post = result.scalar_one()
        return self._post_to_dict(post, False)

    async def toggle_like(self, user_id: int, post_id: str) -> dict:
        pid = int(post_id)

        result = await self.db.execute(
            select(SocialLike).where(SocialLike.user_id == user_id, SocialLike.post_id == pid)
        )
        existing = result.scalar_one_or_none()

        post_result = await self.db.execute(select(SocialPost).where(SocialPost.id == pid))
        post = post_result.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        if existing:
            await self.db.delete(existing)
            post.engagement_count = max(0, post.engagement_count - 1)
            liked = False
        else:
            like = SocialLike(user_id=user_id, post_id=pid, created_at=datetime.now(timezone.utc))
            self.db.add(like)
            post.engagement_count += 1
            liked = True

        await self.db.flush()
        return {"liked": liked, "engagement_count": post.engagement_count}

    async def get_comments(self, post_id: str) -> list[dict]:
        result = await self.db.execute(
            select(SocialComment).where(SocialComment.post_id == int(post_id)).order_by(SocialComment.created_at.asc())
        )
        comments = result.scalars().all()

        output = []
        for c in comments:
            author_result = await self.db.execute(select(User).where(User.id == c.user_id))
            author = author_result.scalar_one_or_none()
            output.append({
                "id": c.id,
                "author": {
                    "id": author.id if author else 0,
                    "username": author.email.split("@")[0] if author else "unknown",
                    "full_name": author.full_name if author else "Unknown",
                    "avatar_url": None,
                },
                "content": c.content,
                "created_at": c.created_at.isoformat() if c.created_at else "",
            })
        return output

    async def add_comment(self, user_id: int, post_id: str, content: str) -> dict:
        pid = int(post_id)
        post_result = await self.db.execute(select(SocialPost).where(SocialPost.id == pid))
        post = post_result.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        comment = SocialComment(post_id=pid, user_id=user_id, content=content)
        self.db.add(comment)
        post.engagement_count += 1
        await self.db.flush()

        author_result = await self.db.execute(select(User).where(User.id == user_id))
        author = author_result.scalar_one()

        return {
            "id": comment.id,
            "author": {"id": author.id, "username": author.email.split("@")[0], "full_name": author.full_name, "avatar_url": None},
            "content": comment.content,
            "created_at": comment.created_at.isoformat() if comment.created_at else "",
        }

    @staticmethod
    def _post_to_dict(post: SocialPost, liked: bool) -> dict:
        return {
            "id": post.id,
            "author": {
                "id": post.user.id,
                "username": post.user.email.split("@")[0] if post.user else "unknown",
                "full_name": post.user.full_name if post.user else "Unknown",
                "avatar_url": None,
            },
            "ticker": post.tickers[0] if post.tickers else "",
            "reasoning": post.content or "",
            "action": post.trade_type or "",
            "risk_level_at_post": "medium",
            "ticker_change_at_post": 0.0,
            "likes_count": post.engagement_count,
            "comments_count": 0,
            "shares_count": 0,
            "liked_by_me": liked,
            "created_at": post.created_at.isoformat() if post.created_at else "",
        }
