from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.recommendation import WhatIfRequest, WhatIfComparisonResponse
from app.services.legal_retriever import LegalRetrieverService
from app.services.explainability_engine import ExplainabilityEngineService
from app.services.whatif_engine import WhatIfEngineService

router = APIRouter(prefix="/whatif", tags=["What-If Scenario Comparison"])


@router.post("/compare", response_model=WhatIfComparisonResponse)
async def compare_scenario_variations(
    payload: WhatIfRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compares two factual variations of a scenario to explain how changes in facts
    affect legal provisions, relevance scores, and evidence.
    """
    # 1. Retrieve candidates for original facts
    orig_provisions = await LegalRetrieverService.retrieve_candidate_provisions(
        payload.original_facts, [], db
    )
    orig_recs = await ExplainabilityEngineService.build_recommendations_with_evidence(
        payload.original_facts, orig_provisions
    )

    # 2. Retrieve candidates for modified facts
    mod_provisions = await LegalRetrieverService.retrieve_candidate_provisions(
        payload.modified_facts, [], db
    )
    mod_recs = await ExplainabilityEngineService.build_recommendations_with_evidence(
        payload.modified_facts, mod_provisions
    )

    # 3. Compute what-if diff and impact
    comparison = await WhatIfEngineService.compare_scenarios(
        payload.original_facts,
        payload.modified_facts,
        orig_recs,
        mod_recs
    )

    return comparison
