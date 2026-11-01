# How to Run NyayaSetu (Legal Assistant)

This guide walks you through setting up and running both the **FastAPI Backend** and the **Flutter Frontend** for the NyayaSetu Indian Constitutional Rights & Legal Assistant platform.

---

## 📋 System Prerequisites

| Component | Minimum Version | Notes |
| :--- | :--- | :--- |
| **Python** | 3.10 or 3.11 | Required for FastAPI backend |
| **Flutter SDK** | 3.22+ (Dart 3.x+) | Required for the frontend app |
| **Web Browser** | Google Chrome or Microsoft Edge | Used for running the Flutter Web UI |
| **Ollama** *(Optional)* | Latest | For local offline LLM generation |
| **Docker** *(Optional)* | Latest | Only needed if using PostgreSQL + pgvector |

---

## 🚀 Quick Start Guide

### Step 1: Start the Backend Server (Terminal 1)

1. Open PowerShell or Terminal and navigate to the `backend` directory:
   ```powershell
   cd "c:\My Repo\legal_assistant\backend"
   ```

2. Activate the existing virtual environment (or create a new one):
   - **Windows:**
     ```powershell
     # If creating fresh: python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     source .venv/bin/activate
     ```

3. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. *(Optional)* Run backend automated tests:
   ```bash
   pytest tests/
   ```

5. Start the backend application:
   ```bash
   python run.py
   ```
   > The API will be live at:
   > - **API Base:** `http://localhost:8000`
   > - **Swagger UI Documentation:** `http://localhost:8000/docs`
   > - **ReDoc:** `http://localhost:8000/redoc`
   > - **Health Check:** `http://localhost:8000/health`

---

### Step 2: Start the Frontend Application (Terminal 2)

1. Open a **second** terminal window and navigate to the `frontend` directory:
   ```powershell
   cd "c:\My Repo\legal_assistant\frontend"
   ```

2. Make sure Flutter is accessible in your terminal.
   *(If Flutter is not in your global `PATH`, add it or reference its binary directly, e.g.: `C:\Users\<user>\Downloads\flutter\bin\flutter.bat`)*

3. Fetch packages and dependencies:
   ```bash
   flutter pub get
   ```

4. *(Optional)* Run frontend tests:
   ```bash
   flutter test
   ```

5. Run the frontend application:
   - **Run on Chrome (Recommended Web Client):**
     ```bash
     flutter run -d chrome --web-port 3000
     ```
   - **Run on Edge:**
     ```bash
     flutter run -d edge --web-port 3000
     ```
   - **Run as Native Windows Desktop App:**
     ```bash
     flutter run -d windows
     ```

   > The application will open at: **`http://localhost:3000`**

---

## ⚙️ Configuration & Environment Settings

The backend configuration is managed via `backend/app/core/config.py` and optional `.env` file in `backend/`:

### Database
- **Default (No Setup Required):** Uses SQLite (`backend/legal_assistant.db`). The database schema and initial Indian Constitution & statutory provisions (Articles 14, 19, 21, 22, 32, 39A, 226, CrPC, IPC/BNS, POSH, etc.) are **automatically created and seeded** on the first server launch.
- **PostgreSQL + pgvector (Optional for production):**
  ```bash
  docker-compose up -d
  ```
  Set `DATABASE_URL="postgresql+asyncpg://legal_user:legal_password@localhost:5432/legal_assistant_db"` in `backend/.env`.

### LLM & RAG Provider
You can configure the reasoning engine in `backend/.env` or `config.py`:
- `LLM_PROVIDER="ollama"` (default local model with automatic fallback to structured deterministic legal analysis)
- `LLM_PROVIDER="gemini"` (requires `LLM_API_KEY`)
- `LLM_PROVIDER="openai"` (requires `OPENAI_API_KEY`)
- `LLM_PROVIDER="deterministic"` (offline rule & template engine)

---

## 🛠️ Troubleshooting

### 1. Flutter command not recognized
If running `flutter` gives `'flutter' is not recognized`:
- Locate your Flutter installation directory (e.g., `C:\Users\<Username>\Downloads\flutter\bin`).
- Add this directory to your Windows User or System Environment `PATH` variable.
- Restart your terminal.

### 2. Port already in use
- **Port 8000 (Backend):** Stop any process listening on 8000 or change the port in `backend/run.py`.
- **Port 3000 (Frontend):** Change `--web-port 3000` to another port such as `--web-port 3001`. If changed, ensure the new origin is listed in `BACKEND_CORS_ORIGINS` in `backend/app/core/config.py`.

### 3. Backend CORS errors
The backend is pre-configured to accept requests from `http://localhost:3000`, `http://localhost:8080`, and `*`.
