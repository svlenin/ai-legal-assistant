"""
Explainability Engine Service.
Maps specific scenario facts to legal provision elements to explain WHY a recommendation was made,
the confidence level, matching factual triggers, and official provenance references.
"""
from typing import List, Tuple
from app.schemas.scenario import ExtractedFacts
from app.models.legal_provision import LegalProvision
from app.schemas.recommendation import RecommendedProvision, LegalProvisionResponse


class ExplainabilityEngineService:
    @classmethod
    async def build_recommendations_with_evidence(
        cls,
        facts: ExtractedFacts,
        scored_candidates: List[Tuple[LegalProvision, float, List[str]]]
    ) -> List[RecommendedProvision]:
        """
        Builds explainable recommendations showing matching facts, reasoning, and provenance.
        """
        recommendations: List[RecommendedProvision] = []

        for prov, score, matched_terms in scored_candidates:
            prov_dto = LegalProvisionResponse.model_validate(prov)

            # Determine confidence level based on score
            if score >= 0.85:
                confidence = "High"
            elif score >= 0.70:
                confidence = "Moderate"
            else:
                confidence = "Contextual"

            # Formulate explainable reasoning based on the match
            why_recommended = cls._generate_reasoning(prov, facts, matched_terms)

            # Formulate matching facts list
            evidence_facts = []
            if facts.legal_issue:
                evidence_facts.append(f"Legal Issue: {facts.legal_issue}")
            if facts.actors:
                evidence_facts.append(f"Involved Parties: {', '.join(facts.actors)}")
            if matched_terms:
                evidence_facts.append(f"Matching Legal Elements: {', '.join(matched_terms[:4])}")
            if facts.key_events:
                evidence_facts.append(f"Scenario Event: {facts.key_events[0]}")

            recommendations.append(
                RecommendedProvision(
                    provision=prov_dto,
                    relevance_score=score,
                    confidence_level=confidence,
                    why_recommended=why_recommended,
                    matching_facts=evidence_facts,
                    provenance_reference=prov.provenance_source_url
                )
            )

        return recommendations

    @staticmethod
    def _generate_reasoning(
        prov: LegalProvision,
        facts: ExtractedFacts,
        matched_terms: List[str]
    ) -> str:
        ident = prov.identifier
        domain = prov.domain_category

        if "Article 22" in ident:
            return (
                "Article 22 directly governs procedural safeguards upon arrest or detention, guaranteeing "
                "the right to know reasons for arrest, access legal counsel, and mandatory production before a magistrate within 24 hours."
            )
        elif "Section 41A" in ident:
            return (
                "Section 41A mandates issuance of a formal notice of appearance rather than routine arrest for offences "
                "with punishment up to 7 years, protecting citizens from arbitrary custodial detention."
            )
        elif "Section 154" in ident:
            return (
                "Section 154 CrPC mandates that police stations must record an FIR upon receiving information of any cognizable offence. "
                "Refusal by police violates binding guidelines established in Lalita Kumari v. Govt of UP."
            )
        elif "Article 21" in ident:
            return (
                "Article 21 guarantees the fundamental right to life and personal liberty, establishing that no person "
                "may be subjected to arbitrary state action, privacy violations, or custodial abuse without fair procedure."
            )
        elif "Article 19(1)(a)" in ident:
            return (
                "Article 19(1)(a) protects freedom of peaceful expression and digital speech against unlawful censorship "
                "unless strictly within the narrow reasonable restrictions of Article 19(2)."
            )
        elif "Article 14" in ident:
            return (
                "Article 14 prohibits unreasonable classification or arbitrary discrimination by government and public bodies, "
                "guaranteeing equal protection before the law."
            )
        elif "Article 32" in ident or "Article 226" in ident:
            return (
                f"{ident} provides direct constitutional remedy through Writs (such as Habeas Corpus or Mandamus) to High Courts / Supreme Court "
                "against illegal custody, arbitrary executive action, or government inaction."
            )
        elif "Consumer Protection" in prov.act_or_document_name or "CPA" in ident:
            return (
                "The Consumer Protection Act entitles consumers to compensation, refund, and replacement for defective products, "
                "deficiency of service, and unfair trade practices."
            )
        elif "Right to Information" in prov.act_or_document_name or "RTI" in ident:
            return (
                "The RTI Act mandates public authorities to disclose government information and official records within 30 days "
                "(or 48 hours for matters of life and liberty)."
            )
        elif "Information Technology" in prov.act_or_document_name or "IT Act" in ident:
            return (
                "The IT Act provides penal and civil remedies against online financial deception, phishing, unauthorized access, "
                "identity theft, and cyber harassment."
            )
        elif "Domestic Violence" in prov.act_or_document_name:
            return (
                "The Protection of Women from Domestic Violence Act provides emergency protection orders, residence rights, "
                "and financial relief through Judicial Magistrates."
            )
        elif "POSH" in prov.act_or_document_name:
            return (
                "The POSH Act mandates formal Internal Complaints Committee (ICC) inquiries and employer protection against workplace harassment."
            )

        matched_str = ", ".join(matched_terms[:3]) if matched_terms else prov.domain_category
        return (
            f"Recommended because your scenario involves {domain.lower()} relating to {facts.legal_issue or 'legal rights'}. "
            f"Key matching elements include: {matched_str}."
        )
