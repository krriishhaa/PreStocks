from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, BigInteger, Date, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
import uuid


class Sector(BaseModel):
    __tablename__ = "sector"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_sector_id = Column(Integer, ForeignKey("sector.id"))
    color_hex = Column(String(7))
    icon_name = Column(String(50))

    parent = relationship("Sector", remote_side="Sector.id")
    companies = relationship("Company", back_populates="sector")


class Tag(BaseModel):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(String(50))
    color_hex = Column(String(7))
