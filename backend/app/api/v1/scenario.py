from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.scenario import ScenarioAnalyzeRequest, ScenarioAnalyzeResponse
from app.services.scenario_analyzer import ScenarioAnalyzerService

router = APIRouter(prefix="/scenario", tags=["Scenario Analysis"])


@router.post("/analyze", response_model=ScenarioAnalyzeResponse)
async def analyze_scenario(payload: ScenarioAnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """
    Extracts facts (actors, events, location, legal issue) and flags urgency/risk.
    """
    response = await ScenarioAnalyzerService.analyze_scenario(
        raw_query=payload.raw_query,
        language=payload.language
    )
    return response
