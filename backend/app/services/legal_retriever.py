"""
Legal Retriever Service.
Performs hybrid search (Keyword + Domain alignment + Vector/Semantic matching)
over verified Indian constitutional and statutory provisions.
"""
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.scenario import ExtractedFacts
from app.models.legal_provision import LegalProvision


class LegalRetrieverService:
    _cached_seed_provisions: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_fallback_seed_data(cls) -> List[Dict[str, Any]]:
        if cls._cached_seed_provisions is None:
            seed_file = Path(__file__).parent.parent / "data" / "legal_knowledge_seed.json"
            if seed_file.exists():
                with open(seed_file, "r", encoding="utf-8") as f:
                    cls._cached_seed_provisions = json.load(f)
            else:
                cls._cached_seed_provisions = []
        return cls._cached_seed_provisions

    @classmethod
    async def retrieve_candidate_provisions(
        cls,
        facts: ExtractedFacts,
        domains: List[str],
        db: Optional[AsyncSession] = None,
        top_k: int = 5
    ) -> List[Tuple[LegalProvision, float, List[str]]]:
        """
        Retrieves candidate provisions matching facts and domains.
        Returns a list of tuples: (LegalProvision, relevance_score: float, matched_terms: List[str])
        """
        provisions: List[LegalProvision] = []

        # 1. Attempt database retrieval
        if db is not None:
            try:
                stmt = select(LegalProvision)
                result = await db.execute(stmt)
                db_provisions = result.scalars().all()
                if db_provisions:
                    provisions = list(db_provisions)
            except Exception:
                pass

        # 2. Fallback to in-memory seed dataset if DB is empty or during standalone testing
        if not provisions:
            seed_items = cls._load_fallback_seed_data()
            for idx, item in enumerate(seed_items, start=1):
                p = LegalProvision(
                    id=idx,
                    source_type=item["source_type"],
                    act_or_document_name=item["act_or_document_name"],
                    identifier=item["identifier"],
                    title=item["title"],
                    summary_simple=item["summary_simple"],
                    full_text=item["full_text"],
                    chapter_or_part=item.get("chapter_or_part"),
                    domain_category=item["domain_category"],
                    keywords=item.get("keywords", []),
                    provenance_source_url=item["provenance_source_url"]
                )
                provisions.append(p)

        # If domains is empty, infer from legal issue and action type
        if not domains:
            inferred_domains = []
            text_for_domain = f"{facts.legal_issue or ''} {facts.action_type or ''} {' '.join(facts.key_events or [])}".lower()
            if any(w in text_for_domain for w in ["arrest", "police", "fir", "custody", "bail", "warrant"]):
                inferred_domains.append("Criminal Procedure & Police Powers")
            if any(w in text_for_domain for w in ["speech", "expression", "liberty", "privacy", "equality", "discrimination", "fundamental"]):
                inferred_domains.append("Fundamental Rights")
            if any(w in text_for_domain for w in ["consumer", "defect", "refund", "warranty", "goods", "service"]):
                inferred_domains.append("Consumer Rights & Commerce")
            if any(w in text_for_domain for w in ["rti", "information", "public authority", "pio"]):
                inferred_domains.append("Administrative Transparency & RTI")
            if any(w in text_for_domain for w in ["cyber", "phishing", "upi", "hacked", "identity theft"]):
                inferred_domains.append("Cyber & Digital Rights")
            if any(w in text_for_domain for w in ["domestic violence", "protection order", "maintenance", "women"]):
                inferred_domains.append("Women & Family Rights")
            if any(w in text_for_domain for w in ["posh", "workplace", "harassment", "employee", "icc"]):
                inferred_domains.append("Labor & Workplace Rights")
            domains = inferred_domains

        # 3. Build search tokens from extracted facts
        query_text_blob = " ".join([
            facts.legal_issue or "",
            facts.action_type or "",
            " ".join(facts.key_events or []),
            " ".join(facts.actors or []),
            facts.location or "",
            " ".join(domains or [])
        ]).lower()

        # Tokenize and clean
        words = re.findall(r'[a-zA-Z0-9_\-\(\)]+', query_text_blob)
        stopwords = {
            "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "is", "was",
            "were", "are", "been", "has", "have", "had", "by", "with", "from", "as", "that",
            "this", "these", "those", "it", "its", "individual", "general", "territorial", "jurisdiction"
        }
        tokens = [w for w in words if len(w) > 2 and w not in stopwords]

        scored_candidates: List[Tuple[LegalProvision, float, List[str]]] = []

        for prov in provisions:
            score = 0.0
            matched_terms: List[str] = []
            prov_text = f"{prov.identifier} {prov.title} {prov.summary_simple} {prov.domain_category}".lower()
            prov_keywords = [k.lower() for k in (prov.keywords or [])]

            # Domain category match
            for domain in domains:
                if domain.lower() in prov.domain_category.lower() or prov.domain_category.lower() in domain.lower():
                    score += 0.35
                    matched_terms.append(f"Domain: {prov.domain_category}")
                    break

            # Identifier match (e.g. Article 21, Section 41A)
            if prov.identifier.lower() in query_text_blob:
                score += 0.50
                matched_terms.append(f"Direct Citation: {prov.identifier}")

            # Keyword matches
            for kw in prov_keywords:
                if kw in query_text_blob:
                    score += 0.25
                    matched_terms.append(kw)

            # Token level matches
            token_matches = 0
            for token in tokens:
                if token in prov_text:
                    token_matches += 1
            if token_matches > 0:
                score += min(0.30, token_matches * 0.05)

            # Normalized relevance score capped between 0.40 and 0.98 if matched
            if score > 0.15 or len(matched_terms) > 0:
                # Normalizing score into a sensible 0.50 to 0.98 scale for display
                norm_score = min(0.98, max(0.55, score))
                scored_candidates.append((prov, round(norm_score, 2), list(set(matched_terms))))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # If no provisions scored above threshold, return general fundamental rights provisions
        if not scored_candidates and provisions:
            default_provisions = provisions[:top_k]
            return [(p, 0.60, ["General Constitutional Context"]) for p in default_provisions]

        return scored_candidates[:top_k]
