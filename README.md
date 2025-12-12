# Socially Backend

A standalone REST API for the **Socially** platform, built with **Python (FastAPI)** and **Oracle Database**.

This project demonstrates a migration from a Prisma/PostgreSQL stack to a Python/Oracle stack, featuring **manual SQL implementation** (no ORM) and custom **JWT Authentication**.

> **Frontend Repository:** The corresponding frontend application is available at [socially-frontend](https://github.com/MeyiGi/socially-frontend)

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.13+
- **Database:** Oracle Database Express Edition (XE)
- **Driver:** python-oracledb (Thin mode)
- **Authentication:** OAuth2 with Password Flow + JWT (Jose, Bcrypt)
- **Testing:** Pytest & HTTPX

## ✨ Features

- **Manual SQL Queries:** All CRUD operations are written in raw SQL.
- **Custom Auth System:** Registration, Login, and Protected Routes without third-party providers (Clerk removed).
- **Post Management:** Create, read, and feed generation.
- **Interactions:** Liking posts (Database schema supports comments/follows).
- **Architecture:** Clean Architecture (Separation of Routes, CRUD, Schemas, and Core logic).

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.13 or higher
- Oracle Database XE (running locally or remotely)

### 2. Installation

Clone the repository and navigate to the folder:

```bash
git clone https://github.com/YOUR_USERNAME/socially-backend.git
cd socially-backend
```

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate it (Linux/macOS)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```ini
# .env
DB_USER=SYSTEM
DB_PASSWORD=your_password
# Ensure the host, port, and SID (xe) match your Oracle setup
DB_DSN=localhost:1522/xe
SECRET_KEY=your_super_secret_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 4. Database Initialization

This project includes a script to automatically create the required tables (users, posts, likes, comments, etc.) in your Oracle database.

**Warning:** This script drops existing tables with the same names.

```bash
python -m app.init_db
```

### 5. Running the Server

Start the development server using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000

## 📖 API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🧪 Testing

Integration tests are included to verify Authentication and Post functionality.

```bash
# Run all tests with verbose output
pytest -v
```

## 📂 Project Structure

```
backend/
├── app/
│   ├── api/v1/         # API Route Controllers
│   ├── core/           # Config, Database Connection, Security
│   ├── crud/           # Manual SQL Queries (Data Access Layer)
│   ├── schemas/        # Pydantic Models (DTOs)
│   ├── main.py         # Entry point
│   └── init_db.py      # Database Setup Script
├── tests/              # Pytest Integration Tests
├── .env                # Secrets
└── pyproject.toml      # Dependencies
```

## ⚠️ Notes for CENG454 Course

- **No ORM Used:** All database interactions in `app/crud/` utilize `cursor.execute()` with raw SQL.
- **Authentication:** Implemented manually in `app/core/security.py` using bcrypt for hashing and python-jose for JWT generation.
- **Oracle LOBs:** Special handling added for Oracle CLOB data types in JSON responses.

## 📝 License

This project is created for educational purposes as part of the CENG454 course.

## 🤝 Contributing

This is an academic project. For any questions or suggestions, please open an issue.

---

**Happy Coding!** 🚀