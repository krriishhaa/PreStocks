from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class LearningModule(BaseModel):
    __tablename__ = "learning_module"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500))
    required_tier = Column(String(50))  # 'beginner', 'intermediate', 'advanced'
    content_url = Column(String(500))  # Link to video or interactive content
    estimated_duration_minutes = Column(Integer)
    quiz_questions = Column(JSON)  # Array of question objects
    order = Column(Integer)  # Order in tier progression

    # Relationships
    user_progress = relationship("UserModuleProgress", back_populates="module")


class UserModuleProgress(BaseModel):
    __tablename__ = "user_module_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    module_id = Column(Integer, ForeignKey("learning_module.id"))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    quiz_score = Column(Integer)  # 0-100, NULL if not completed

    # Relationships
    user = relationship("User", back_populates="module_progress")
    module = relationship("LearningModule", back_populates="user_progress")
