from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class NewsArticle(BaseModel):
    __tablename__ = "news_article"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    source_name = Column(String(100))
    source_url = Column(Text)
    article_url = Column(Text, nullable=False)
    image_url = Column(Text)
    author = Column(String(255))
    published_at = Column(DateTime, nullable=False)
    category = Column(String(50))
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    relevance_score = Column(Float)
    is_breaking = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSONB, default={})

    companies = relationship("Company", secondary="news_company", lazy="selectin")


class NewsCompany(Base):
    __tablename__ = "news_company"

    news_id = Column(Integer, ForeignKey("news_article.id", ondelete="CASCADE"), primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), primary_key=True)
    relevance = Column(Float, default=1.0)


class NewsSector(Base):
    __tablename__ = "news_sector"

    news_id = Column(Integer, ForeignKey("news_article.id", ondelete="CASCADE"), primary_key=True)
    sector_id = Column(Integer, ForeignKey("sector.id", ondelete="CASCADE"), primary_key=True)
