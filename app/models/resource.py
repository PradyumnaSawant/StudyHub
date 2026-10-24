from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), index=True, nullable=False) # notes, PYQ, question_bank, revision
    subject_id = Column(Integer, ForeignKey("course_subjects.id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(String(50), nullable=True) # e.g. "2.4 MB"
    syllabus_tag = Column(String(50), index=True, nullable=False) # e.g. "Unit 1: Trees & Graphs", "2024 Pattern"
    verification_status = Column(String(30), default="pending", index=True, nullable=False) # pending, verified, outdated, rejected
    upload_date = Column(DateTime, default=datetime.utcnow)
    download_count = Column(Integer, default=0)
    ai_summary = Column(Text, nullable=True) # Cache for generated AI summary

    # Relationships
    subject = relationship("CourseSubject", back_populates="resources")
    uploader = relationship("User", back_populates="resources")
    bookmarks = relationship("Bookmark", back_populates="resource", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="resource", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="resource", cascade="all, delete-orphan")
