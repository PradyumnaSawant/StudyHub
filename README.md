# StudyHub 🎓📚

> **A centralized, syllabus-aligned study material platform designed specifically for engineering students.**

StudyHub simplifies finding, sharing, and organizing verified academic resources—such as lecture notes, previous years' question papers (PYQs), formula sheets, and presentations—mapped directly to semester, department, and syllabus versions.

---

## 🌟 Key Features

- **Role-Based Access Control (RBAC):**
  - **Students:** Browse syllabus-aligned subjects, upload study materials, bookmark resources, download files, and request AI summaries.
  - **Verifiers / Faculty:** Review pending uploads, verify accuracy and syllabus relevance, flag quality issues, and approve content.
  - **Administrators:** Platform-wide oversight, manage courses, track user activity, view reports, and manage verified content.
- **Syllabus & Course Mapping:** Resources are organized strictly by Engineering Stream (CSE, ECE, ME, etc.), Semester, and Subject Code.
- **AI-Powered Summaries:** Integrated LLM capability (Anthropic Claude / OpenAI) for generating instant, bulleted summaries of lengthy study resources.
- **Smart Resource Search:** Instant filtering and full-text search across titles, descriptions, courses, and resource types.
- **Modern Responsive UI:** Glassmorphism-inspired design crafted with Jinja2 templates, HTMX for seamless asynchronous UI interactions without page reloads, and modern CSS.
- **Local & Swappable Storage:** Modular file storage system currently managing local uploads, easily extensible to AWS S3 or Cloudflare R2.

---

## 🛠️ Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Server:** [Uvicorn](https://www.uvicorn.org/) (ASGI)
- **Database:** SQLite (MVP default) with [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- **Data Validation & Settings:** [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Authentication:** JWT tokens via `PyJWT` and password hashing with `passlib[bcrypt]`
- **Frontend:** [Jinja2](https://jinja.palletsprojects.com/) Templates + [HTMX](https://htmx.org/)
- **Testing:** `pytest` + `httpx`

---

## 📁 Project Structure

```text
studyhub/
├── app/
│   ├── core/           # Core configs, DB connection, JWT & security helpers
│   ├── models/         # SQLAlchemy database models (User, Resource, Course, etc.)
│   ├── schemas/        # Pydantic validation schemas
│   ├── routers/        # FastAPI endpoints (auth, dashboard, resources, verifiers, admin)
│   ├── services/       # Business logic (file storage, AI summarizer, search engine)
│   ├── static/         # CSS styles and uploaded resource files
│   └── templates/      # Jinja2 HTML templates & HTMX partial views
├── .env.example        # Template for environment configuration
├── requirements.txt    # Python dependencies
├── run.py              # Application entry point
├── seed.py             # Database initialization and sample data generator
├── studyhub.db         # SQLite database file
└── test_app.py         # Automated test suite
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- Git (optional, if cloning from a repository).

### 2. Clone and Setup Environment

```bash
# Navigate to the project root
cd studyhub

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Review or edit the `.env` file settings:
```env
PROJECT_NAME="StudyHub"
SECRET_KEY="studyhub-super-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL="sqlite:///./studyhub.db"
UPLOAD_DIR="./app/static/uploads"

# Optional: Add your API key for AI summaries
ANTHROPIC_API_KEY=""
OPENAI_API_KEY=""
```

### 5. Seed the Database

Initialize tables and populate default sample users, engineering courses, and study materials:

```bash
python seed.py
```

### 6. Run the Application

Start the development server using Uvicorn:

```bash
python run.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 👥 Default Demo Accounts

You can log in directly using the pre-seeded credentials:

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@studyhub.edu` | `admin123` | Full admin privileges & system stats |
| **Verifier** | `faculty.verifier@studyhub.edu` | `verifier123` | Faculty verification & approval portal |
| **Student (CSE)** | `kamonmi@student.edu` | `student123` | 3rd Sem Computer Science student |
| **Student (ECE)** | `sarah.ece@student.edu` | `student123` | 4th Sem Electronics student |

---

## 🧪 Running Tests

To run the automated test suite:

```bash
pytest test_app.py -v
```

---

## 🗺️ Roadmap & Future Enhancements

- [ ] PostgreSQL migration with Full-Text Search (tsvector / pg_trgm).
- [ ] Direct AWS S3 / Cloudflare R2 cloud storage integration.
- [ ] Push notifications & alerts for new subject materials.
- [ ] Native dark/light mode toggle.
- [ ] Discussion forums / question-and-answer threads per resource.

---

## 📄 License

This project is licensed under the MIT License. Feel free to use and modify it for academic or personal projects.
