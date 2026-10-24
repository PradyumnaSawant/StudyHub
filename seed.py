import os
from sqlalchemy.orm import Session
from app.core.database import engine, Base, SessionLocal
from app.core.security import hash_password
from app.models import User, CourseSubject, Resource, Bookmark, Verification, Report

def seed_database():
    print("[INFO] Initializing StudyHub Database Schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        print("[INFO] Seeding Initial Platform Users...")
        # 1. Admin
        admin = User(
            name="Dr. Alan Turing",
            email="admin@studyhub.edu",
            password_hash=hash_password("admin123"),
            role="Admin",
            college="MIT Institute of Technology",
            course="CSE",
            semester=8
        )
        # 2. Verifier / Faculty
        verifier = User(
            name="Prof. Eleanor Vance",
            email="faculty.verifier@studyhub.edu",
            password_hash=hash_password("verifier123"),
            role="Verifier",
            college="MIT Institute of Technology",
            course="CSE",
            semester=6
        )
        # 3. Student (CSE)
        student_cse = User(
            name="Kamonmi",
            email="kamonmi@student.edu",
            password_hash=hash_password("student123"),
            role="Student",
            college="MIT Institute of Technology",
            course="CSE",
            semester=3
        )
        # 4. Student (ECE)
        student_ece = User(
            name="Sarah Jenkins",
            email="sarah.ece@student.edu",
            password_hash=hash_password("student123"),
            role="Student",
            college="State Engineering University",
            course="ECE",
            semester=4
        )

        db.add_all([admin, verifier, student_cse, student_ece])
        db.commit()

        print("[INFO] Seeding Engineering Course Subjects...")
        subjects = [
            CourseSubject(name="Data Structures & Algorithms", code="CS201", syllabus_version="2024", department="CSE", semester=3),
            CourseSubject(name="Operating Systems", code="CS301", syllabus_version="2024", department="CSE", semester=4),
            CourseSubject(name="Database Management Systems", code="CS302", syllabus_version="2024", department="CSE", semester=4),
            CourseSubject(name="Artificial Intelligence & Machine Learning", code="CS401", syllabus_version="2024", department="CSE", semester=7),
            CourseSubject(name="Signals & Digital Systems", code="EC201", syllabus_version="2024", department="ECE", semester=3),
            CourseSubject(name="Microprocessors & Microcontrollers", code="EC301", syllabus_version="2022", department="ECE", semester=5),
            CourseSubject(name="Fluid Mechanics & Thermodynamics", code="ME201", syllabus_version="2024", department="MECH", semester=3),
            CourseSubject(name="Structural Mechanics & Design", code="CE201", syllabus_version="2024", department="CIVIL", semester=3),
        ]
        db.add_all(subjects)
        db.commit()

        # Create dummy physical files under static/uploads
        upload_dir = "./app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        sample_file_1 = os.path.join(upload_dir, "dsa_trees_graphs_notes.pdf")
        sample_file_2 = os.path.join(upload_dir, "dbms_sql_pyq_2024.pdf")
        sample_file_3 = os.path.join(upload_dir, "os_concurrency_revision.pdf")

        sample_content = b"%PDF-1.4 %StudyHub Verified Sample Engineering Note Document\n1 0 obj << /Title (StudyHub Engineering Material) >> endobj\nxref\n0 1\n0000000000 65535 f \ntrailer << /Root 1 0 R >>\n%%EOF"
        for path in [sample_file_1, sample_file_2, sample_file_3]:
            with open(path, "wb") as f:
                f.write(sample_content)

        print("[INFO] Seeding Verified & Pending Study Resources...")
        resources = [
            Resource(
                title="Unit 3: Graph Algorithms (Dijkstra, Kruskal, Prim's) & BST Traversals",
                description="Comprehensive handwritten faculty lecture notes covering graph representations (Adjacency Matrix/List), shortest path algorithms, MST, and AVL Tree rotations with solved numerical examples.",
                type="notes",
                subject_id=subjects[0].id, # CS201
                uploader_id=verifier.id,
                file_url="/static/uploads/dsa_trees_graphs_notes.pdf",
                file_size="2.8 MB",
                syllabus_tag="Unit 3: Graphs & Trees (2024 Pattern)",
                verification_status="verified",
                download_count=142
            ),
            Resource(
                title="DBMS 2024 End-Semester Solved PYQ & Normalization Practice Set",
                description="Previous 5 years solved university examination papers including 1NF, 2NF, 3NF, BCNF decomposition step-by-step solutions and SQL joins query cheat sheet.",
                type="PYQ",
                subject_id=subjects[2].id, # CS302
                uploader_id=student_cse.id,
                file_url="/static/uploads/dbms_sql_pyq_2024.pdf",
                file_size="4.1 MB",
                syllabus_tag="Unit 4: Relational Normalization & SQL",
                verification_status="verified",
                download_count=215
            ),
            Resource(
                title="Operating Systems: Process Synchronization & Deadlock Prevention Formula Sheet",
                description="Last-minute 4-page revision sheet for Bankers Algorithm, Mutex locks, Semaphores, Reader-Writer problem, and Memory Paging algorithms.",
                type="revision",
                subject_id=subjects[1].id, # CS301
                uploader_id=student_cse.id,
                file_url="/static/uploads/os_concurrency_revision.pdf",
                file_size="1.4 MB",
                syllabus_tag="Unit 2: Process Concurrency & Deadlocks",
                verification_status="pending",
                download_count=45
            ),
            Resource(
                title="Signals & Systems: Fourier Transform & Z-Transform Question Bank",
                description="100+ practice questions with step-by-step solutions for ECE Semester 3 mid-sem preparation.",
                type="question_bank",
                subject_id=subjects[4].id, # EC201
                uploader_id=student_ece.id,
                file_url="/static/uploads/dsa_trees_graphs_notes.pdf",
                file_size="3.2 MB",
                syllabus_tag="Unit 2: Continuous & Discrete Fourier Transform",
                verification_status="verified",
                download_count=89
            )
        ]
        db.add_all(resources)
        db.commit()

        print("[INFO] Seeding Sample Bookmarks & Verifications...")
        b1 = Bookmark(user_id=student_cse.id, resource_id=resources[0].id)
        b2 = Bookmark(user_id=student_cse.id, resource_id=resources[1].id)
        v1 = Verification(
            resource_id=resources[0].id,
            verifier_id=verifier.id,
            status="verified",
            comments="Verified against 2024 syllabus pattern. Derivations and numerical examples are accurate."
        )
        db.add_all([b1, b2, v1])
        db.commit()

        print("[SUCCESS] Database Seeding Complete!")
        print("\nDefault Logins:")
        print(" - Student:  kamonmi@student.edu / student123")
        print(" - Verifier: faculty.verifier@studyhub.edu / verifier123")
        print(" - Admin:    admin@studyhub.edu / admin123\n")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
