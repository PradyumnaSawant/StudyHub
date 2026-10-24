from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Resource, CourseSubject

class SearchService:
    @staticmethod
    def search_resources(
        db: Session,
        query: Optional[str] = None,
        department: Optional[str] = None,
        subject_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        syllabus_version: Optional[str] = None,
        verified_only: bool = False
    ) -> List[Resource]:
        """
        Executes modular search & filter against SQLite/PostgreSQL models.
        Can be upgraded to Elasticsearch/Meilisearch by replacing this service logic.
        """
        q = db.query(Resource).join(CourseSubject)

        if verified_only:
            q = q.filter(Resource.verification_status == "verified")

        if department and department != "All":
            q = q.filter(CourseSubject.department == department)

        if subject_id and subject_id > 0:
            q = q.filter(Resource.subject_id == subject_id)

        if resource_type and resource_type != "All":
            q = q.filter(Resource.type == resource_type)

        if syllabus_version and syllabus_version != "All":
            q = q.filter(CourseSubject.syllabus_version == syllabus_version)

        if query:
            search_term = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Resource.title.ilike(search_term),
                    Resource.description.ilike(search_term),
                    Resource.syllabus_tag.ilike(search_term),
                    CourseSubject.name.ilike(search_term),
                    CourseSubject.code.ilike(search_term)
                )
            )

        # Order by verification priority, then upload date desc
        return q.order_by(Resource.upload_date.desc()).all()
