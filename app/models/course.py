from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class CourseSubject(Base):
    __tablename__ = "course_subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False) # e.g. Data Structures & Algorithms
    code = Column(String(20), index=True, nullable=False) # e.g. CS201
    syllabus_version = Column(String(20), nullable=False) # e.g. 2024
    department = Column(String(50), index=True, nullable=False) # e.g. CSE, ECE, MECH, CIVIL
    semester = Column(Integer, default=1, nullable=False)

    # Relationships
    resources = relationship("Resource", back_populates="subject", cascade="all, delete-orphan")
