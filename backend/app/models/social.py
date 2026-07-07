from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class SocialPost(BaseModel):
    __tablename__ = "social_post"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    content = Column(Text)  # User's reasoning, <300 chars
    tickers = Column(ARRAY(String))  # Array of tickers mentioned
    trade_type = Column(String(10))  # 'buy', 'sell', 'hold'

    # Relationships
    user = relationship("User", back_populates="social_posts")
    comments = relationship("SocialComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("SocialLike", back_populates="post", cascade="all, delete-orphan")


class SocialComment(BaseModel):
    __tablename__ = "social_comment"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_post.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    content = Column(Text)

    # Relationships
    post = relationship("SocialPost", back_populates="comments")


class SocialLike(BaseModel):
    __tablename__ = "social_like"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_post.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))

    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_post_like'),)

    # Relationships
    post = relationship("SocialPost", back_populates="likes")
