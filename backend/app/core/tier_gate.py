"""
Tier-based access gating.
Controls feature access based on user's learning tier.
"""
from fastapi import HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.database.session import get_db
from app.models.user import User


TIER_LEVELS = {"beginner": 1, "intermediate": 2, "advanced": 3}


class TierGate:
    """Dependency that enforces minimum tier requirements."""

    def __init__(self, minimum_tier: str):
        self.minimum_tier = minimum_tier
        self.minimum_level = TIER_LEVELS.get(minimum_tier, 1)

    async def __call__(
        self,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
    ) -> int:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user_level = TIER_LEVELS.get(user.risk_tier or "beginner", 1)

        if user_level < self.minimum_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {self.minimum_tier} tier or above. Complete learning modules to unlock.",
            )

        return user_id


# Pre-configured gates for common use
require_beginner = TierGate("beginner")
require_intermediate = TierGate("intermediate")
require_advanced = TierGate("advanced")
