from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router as api_v1_router


from app.data.seed_db import seed_knowledge_base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if using SQLite for dev testing and seed provisions
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_knowledge_base()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Explainable Indian Constitutional Rights & Legal Information Recommendation System API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.APP_ENV
    }


@app.get("/", tags=["Root"])
async def root_endpoint():
    return {
        "message": "Welcome to the Explainable Indian Constitutional Rights & Legal Information System API",
        "docs_url": "/docs",
        "health_check": "/health",
        "disclaimer": settings.DISCLAIMER_TEXT
    }
