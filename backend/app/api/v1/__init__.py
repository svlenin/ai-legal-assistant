from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.scenario import router as scenario_router
from app.api.v1.recommendation import router as rec_router
from app.api.v1.constitution import router as const_router
from app.api.v1.whatif import router as whatif_router
from app.api.v1.bookmarks import router as bookmark_router
from app.api.v1.quiz import router as quiz_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(scenario_router)
api_router.include_router(rec_router)
api_router.include_router(const_router)
api_router.include_router(whatif_router)
api_router.include_router(bookmark_router)
api_router.include_router(quiz_router)
