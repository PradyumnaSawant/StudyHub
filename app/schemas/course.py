from pydantic import BaseModel, ConfigDict
from typing import Optional

class CourseSubjectCreate(BaseModel):
    name: str
    code: str
    syllabus_version: str = "2024"
    department: str # CSE, ECE, MECH, CIVIL
    semester: int = 1

class CourseSubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    syllabus_version: str
    department: str
    semester: int

    model_config = ConfigDict(from_attributes=True)
