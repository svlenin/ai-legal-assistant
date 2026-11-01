"""
What-If Scenario Counterfactual Engine.
Detects factual deltas between two scenarios, evaluates changes in provision applicability,
and explains the exact legal implications of modifying factual parameters.
"""
from typing import List, Dict, Set
from app.schemas.scenario import ExtractedFacts
from app.schemas.recommendation import WhatIfComparisonResponse, RecommendedProvision


class WhatIfEngineService:
    @classmethod
    async def compare_scenarios(
        cls,
        original_facts: ExtractedFacts,
        modified_facts: ExtractedFacts,
        original_provisions: List[RecommendedProvision],
        updated_provisions: List[RecommendedProvision]
    ) -> WhatIfComparisonResponse:
        """
        Produces an explainable diff summary of factual changes and statutory impacts.
        """
        changes_detected: List[str] = []

        # 1. Compare actors
        orig_actors_set = set(original_facts.actors or [])
        mod_actors_set = set(modified_facts.actors or [])
        added_actors = mod_actors_set - orig_actors_set
        removed_actors = mod_actors_set - orig_actors_set
        if added_actors or removed_actors:
            desc = f"Actor shift: "
            if added_actors:
                desc += f"Added [{', '.join(added_actors)}] "
            if removed_actors:
                desc += f"Removed [{', '.join(removed_actors)}]"
            changes_detected.append(desc.strip())

        # 2. Compare legal issue or action type
        if original_facts.legal_issue != modified_facts.legal_issue and modified_facts.legal_issue:
            changes_detected.append(f"Legal issue shifted from '{original_facts.legal_issue}' to '{modified_facts.legal_issue}'")

        if original_facts.action_type != modified_facts.action_type and modified_facts.action_type:
            changes_detected.append(f"Action context changed to '{modified_facts.action_type}'")

        # 3. Compare key timeline events
        if original_facts.key_events != modified_facts.key_events:
            changes_detected.append("Timeline events and factual narrative modified")

        # 4. Compare location
        if original_facts.location != modified_facts.location and modified_facts.location:
            changes_detected.append(f"Jurisdiction/Location updated to '{modified_facts.location}'")

        # 5. Provision impact evaluation
        orig_prov_map = {p.provision.identifier: p for p in original_provisions}
        mod_prov_map = {p.provision.identifier: p for p in updated_provisions}

        newly_applicable: List[str] = []
        no_longer_applicable: List[str] = []
        score_shifts: List[str] = []

        for ident, mod_p in mod_prov_map.items():
            if ident not in orig_prov_map:
                newly_applicable.append(f"{ident} ({mod_p.provision.title})")
            else:
                orig_score = orig_prov_map[ident].relevance_score
                delta = round(mod_p.relevance_score - orig_score, 2)
                if abs(delta) >= 0.05:
                    trend = "increased" if delta > 0 else "decreased"
                    score_shifts.append(f"{ident}: Relevance {trend} by {abs(delta):.2f}")

        for ident, orig_p in orig_prov_map.items():
            if ident not in mod_prov_map:
                no_longer_applicable.append(f"{ident} ({orig_p.provision.title})")

        # 6. Synthesize comprehensive diff summary
        diff_points = []
        if newly_applicable:
            diff_points.append(f"Newly applicable provisions: {', '.join(newly_applicable)}.")
        if no_longer_applicable:
            diff_points.append(f"Provisions no longer directly triggered: {', '.join(no_longer_applicable)}.")
        if score_shifts:
            diff_points.append(f"Confidence/Relevance score changes: {'; '.join(score_shifts)}.")

        if not diff_points:
            diff_points.append("The factual modifications did not materially change the primary applicable constitutional provisions.")

        diff_summary = (
            f"Factual Change Analysis:\n"
            f"- Factual deltas detected: {len(changes_detected)}\n"
            f"- Legal impact: {' '.join(diff_points)}"
        )

        return WhatIfComparisonResponse(
            original_provisions=original_provisions,
            updated_provisions=updated_provisions,
            diff_summary=diff_summary,
            changes_detected=changes_detected or ["Minor wording delta; core factual parameters remain constant."]
        )
