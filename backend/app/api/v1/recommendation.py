from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.schemas.scenario import ScenarioAnalyzeRequest
from app.schemas.recommendation import RecommendationResponse
from app.services.scenario_analyzer import ScenarioAnalyzerService
from app.services.legal_retriever import LegalRetrieverService
from app.services.rag_engine import RAGEngineService
from app.services.explainability_engine import ExplainabilityEngineService

router = APIRouter(prefix="/recommendations", tags=["Legal Recommendations"])


@router.post("/explain", response_model=RecommendationResponse)
async def get_explainable_recommendations(
    payload: ScenarioAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    End-to-end explainable recommendation endpoint:
    Fact Extraction -> Controlled Retrieval -> Evidence Trail -> Grounded Plain Language Explanation.
    """
    # 1. Analyze facts
    analysis = await ScenarioAnalyzerService.analyze_scenario(payload.raw_query, payload.language)

    # 2. Retrieve verified candidate provisions
    candidate_provisions = await LegalRetrieverService.retrieve_candidate_provisions(
        analysis.extracted_facts,
        analysis.identified_domains,
        db
    )

    # 3. Build explainability trail
    recommendations = await ExplainabilityEngineService.build_recommendations_with_evidence(
        analysis.extracted_facts,
        candidate_provisions
    )

    # 4. Generate grounded RAG plain-language explanation
    explanation = await RAGEngineService.generate_explanation(
        analysis.extracted_facts,
        candidate_provisions,
        payload.language
    )

    return RecommendationResponse(
        scenario_id=None,
        extracted_facts=analysis.extracted_facts,
        disclaimer=settings.DISCLAIMER_TEXT,
        risk_level=analysis.risk_level,
        recommendations=recommendations,
        plain_language_explanation=explanation,
        follow_up_questions=analysis.clarification_questions
    )
