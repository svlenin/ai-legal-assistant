# Explainable AI-Based Indian Constitutional Rights & Legal Information Recommendation System (NyayaSetu)

## Project Overview
An explainable AI-powered Indian legal information and constitutional rights assistant designed for Indian citizens. The system analyzes user legal/constitutional scenarios, extracts structured facts, retrieves verified Indian constitutional Articles, Acts, and Sections from a controlled legal knowledge base, generates plain-language explanations with strict provenance citations, provides explainability rationales ("Why recommended"), and enables "What-If" counterfactual scenario comparisons.

---

## Core Architecture & Engine Pipeline

```
User Scenario Input
       │
       ▼
1. Scenario Analyzer (Fact Extraction: Actors, Events, Timeline, Location, Legal Issue)
       │
       ▼
2. Legal Domain Classifier & Risk Detection (Urgency / Professional Counsel Advisories)
       │
       ▼
3. Controlled Hybrid Retriever (PostgreSQL Full-Text Search + pgvector Semantic Embeddings)
       │
       ▼
4. Relevant Provision Ranking & Verification Filter (Verified Knowledge Base Only)
       │
       ▼
5. Explainability Engine (Evidence Trail Mapping Facts to Legal Elements)
       │
       ▼
6. Grounded RAG Generator (Plain-Language Explanation strictly referencing retrieved context)
       │
       ▼
7. What-If Counterfactual Engine (Fact modification & Provision Delta Comparison)
```

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Flutter, Dart 3.12, Material 3, Google Fonts |
| **Backend API** | Python 3.11, FastAPI, Pydantic v2, Uvicorn |
| **Database & Vector Search** | PostgreSQL 16 + `pgvector`, SQLAlchemy (async) |
| **Orchestration & RAG** | LangChain / Custom Explainability & What-If Engines |
| **Authentication** | JWT (OAuth2 Bearer Token) |
| **API Protocol** | RESTful JSON over HTTP |

---

## Project Structure

```
legal_assistant/
├── docker-compose.yml              # PostgreSQL + pgvector container
├── backend/                        # FastAPI Python Backend
│   ├── .env.example                # Environment variables template
│   ├── requirements.txt            # Python dependencies
│   ├── run.py                      # Local server runner (port 8000)
│   ├── app/
│   │   ├── main.py                 # FastAPI initialization & CORS
│   │   ├── core/                   # Config, Database, JWT Security
│   │   ├── models/                 # SQLAlchemy ORM Models
│   │   ├── schemas/                # Pydantic Request/Response DTOs
│   │   ├── api/v1/                 # Endpoints (Auth, Scenario, Recs, What-If, Quiz, Bookmarks)
│   │   └── services/               # Scenario Analyzer, Retriever, RAG, Explainability, What-If
│   └── tests/                      # Automated pytest suite
│
└── frontend/                       # Flutter Material 3 Client
    ├── pubspec.yaml                # Flutter dependencies
    ├── lib/
    │   ├── main.dart               # App entrypoint & Theme
    │   ├── core/                   # Theme, Colors, API Constants, Legal Disclaimers
    │   ├── data/                   # Models & ApiService HTTP client
    │   └── presentation/           # Material 3 Screens & Components
    └── test/                       # Flutter widget tests
```

---

## Quickstart Guide

> For a complete, step-by-step setup guide with troubleshooting, see **[HOW_TO_RUN.md](HOW_TO_RUN.md)**.

### 1. Backend Setup & Execution
```bash
# Navigate to backend and activate virtual environment
cd backend
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run automated tests
pytest tests/

# Start FastAPI dev server
python run.py
# Server will run at http://localhost:8000 (Swagger docs at http://localhost:8000/docs)
```

### 2. Frontend Execution
```bash
cd frontend
flutter pub get
flutter test
flutter run
```

### 3. Database (Optional Docker PostgreSQL + pgvector)
```bash
docker-compose up -d
```
