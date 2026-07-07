from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class Alert(BaseModel):
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    company_id = Column(Integer, ForeignKey("company.id"))
    alert_type = Column(String(50), nullable=False)
    condition = Column(JSONB, nullable=False)
    title = Column(String(255))
    message = Column(Text)
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime)
    cooldown_hours = Column(Integer, default=24)
    last_notified_at = Column(DateTime)

    user = relationship("User", backref="alerts")
    company = relationship("Company")


class Notification(BaseModel):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    alert_id = Column(Integer, ForeignKey("alert.id"))
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, default={})
    channel = Column(String(20), default="in_app")
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)

    user = relationship("User", backref="notifications")
    alert = relationship("Alert")
