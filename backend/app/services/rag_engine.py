"""
RAG Engine Service.
Generates grounded, plain-language legal explanations strictly synthesized from retrieved statutory provisions.
Supports Local LLM execution via Ollama (Llama 3, Mistral, Qwen, etc.) with automatic fallback.
"""
from typing import List, Tuple
import logging
import httpx
from app.core.config import settings
from app.schemas.scenario import ExtractedFacts
from app.models.legal_provision import LegalProvision

logger = logging.getLogger(__name__)


class RAGEngineService:
    @classmethod
    async def generate_explanation(
        cls,
        facts: ExtractedFacts,
        scored_candidates: List[Tuple[LegalProvision, float, List[str]]],
        language: str = "en"
    ) -> str:
        """
        Synthesizes a structured plain-language guide based on extracted facts and retrieved provisions.
        Uses local Ollama if configured, falling back to deterministic synthesis if offline.
        """
        if not scored_candidates:
            return (
                "Based on the provided details, no direct statutory match was found in the initial database pass. "
                "Please verify if public authorities, specific consumer contracts, or criminal allegations were involved."
            )

        # 1. If Ollama provider is enabled, attempt local LLM synthesis
        if settings.LLM_PROVIDER.lower() == "ollama":
            ollama_response = await cls._generate_with_ollama(facts, scored_candidates, language)
            if ollama_response:
                return ollama_response

        # 2. Deterministic grounded synthesis fallback
        return cls._generate_deterministic_explanation(facts, scored_candidates)

    @classmethod
    async def _generate_with_ollama(
        cls,
        facts: ExtractedFacts,
        scored_candidates: List[Tuple[LegalProvision, float, List[str]]],
        language: str = "en"
    ) -> str | None:
        """
        Calls local Ollama instance (e.g. http://localhost:11434/api/generate).
        """
        # Format context from verified provisions
        context_blocks = []
        for prov, score, terms in scored_candidates[:4]:
            context_blocks.append(
                f"[{prov.identifier} - {prov.act_or_document_name}]\n"
                f"Title: {prov.title}\n"
                f"Summary: {prov.summary_simple}\n"
                f"Statutory Text: {prov.full_text}\n"
            )
        retrieved_context = "\n---\n".join(context_blocks)

        prompt = (
            f"You are Legal Assistant, an explainable Indian Legal Information and Constitutional Rights Assistant.\n"
            f"Explain the user's legal rights clearly and concisely in plain language, strictly based on the provided verified legal context.\n"
            f"DO NOT cite nonexistent laws or hallucinate penalties.\n\n"
            f"### EXTRACTED SCENARIO FACTS:\n"
            f"- Legal Issue: {facts.legal_issue or 'Constitutional & Legal Rights'}\n"
            f"- Involved Parties/Actors: {', '.join(facts.actors or ['Citizen'])}\n"
            f"- Key Events: {' | '.join(facts.key_events or [])}\n"
            f"- Jurisdiction: {facts.location or 'India'}\n\n"
            f"### VERIFIED RETRIEVED LEGAL CONTEXT:\n"
            f"{retrieved_context}\n\n"
            f"### INSTRUCTIONS:\n"
            f"Structure your response with the following markdown headings:\n"
            f"### Situation Summary\n"
            f"### Primary Applicable Legal Foundations (cite specific Articles/Sections from context)\n"
            f"### Actionable Safeguards & Procedural Rights\n"
            f"### Important Notice (state that this is educational legal information, not formal legal counsel)\n"
        )

        try:
            print(f"[LLM] Calling Ollama model '{settings.OLLAMA_MODEL}' at {settings.OLLAMA_BASE_URL}...")
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
                res = await client.post(
                    f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "top_p": 0.9,
                        }
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    output_text = data.get("response", "").strip()
                    if output_text:
                        print(f"[LLM] SUCCESS: Response received from Ollama '{settings.OLLAMA_MODEL}' ({len(output_text)} characters).")
                        return output_text
                else:
                    print(f"[LLM] WARNING: Ollama returned HTTP {res.status_code}.")
                    logger.warning(f"Ollama returned HTTP status {res.status_code}: {res.text}")
        except Exception as e:
            print(f"[LLM] NOTICE: Ollama not reachable ({e}). Using grounded deterministic template.")
            logger.info(f"Ollama not reachable ({e}). Using grounded deterministic template.")

        return None

    @classmethod
    def _generate_deterministic_explanation(
        cls,
        facts: ExtractedFacts,
        scored_candidates: List[Tuple[LegalProvision, float, List[str]]]
    ) -> str:
        top_provs = [item[0] for item in scored_candidates[:3]]
        prov_citations = ", ".join([f"{p.identifier} ({p.act_or_document_name})" for p in top_provs])

        # Domain-specific procedural guidance
        procedural_steps = []
        for p in top_provs:
            if "Article 22" in p.identifier or "Section 41A" in p.identifier:
                procedural_steps.append(
                    "• **Right upon Arrest / Summons**: You have the constitutional right to demand the written grounds for arrest, "
                    "contact an advocate or family member immediately, and insist on being produced before a Magistrate within 24 hours."
                )
            elif "Section 154" in p.identifier:
                procedural_steps.append(
                    "• **FIR Registration Remedy**: If the local police station refuses to file an FIR for a cognizable matter, "
                    "you can send a written complaint via registered post to the Superintendent of Police (SP) or file an application before the Magistrate under Section 156(3) CrPC / 175(3) BNSS."
                )
            elif "Article 21" in p.identifier:
                procedural_steps.append(
                    "• **Protection of Liberty & Privacy**: Any state coercion, search, or physical restraint must adhere strictly to fair, "
                    "just, and non-arbitrary legal procedures established by law (Maneka Gandhi doctrine)."
                )
            elif "Consumer Protection" in p.act_or_document_name:
                procedural_steps.append(
                    "• **Consumer Redressal Step**: Send a formal grievance/notice to the company. If unresolved, file an online consumer complaint "
                    "via the e-Daakhil portal (edaakhil.nic.in) or call National Consumer Helpline (1915)."
                )
            elif "Right to Information" in p.act_or_document_name:
                procedural_steps.append(
                    "• **RTI Appeal**: If the Public Information Officer (PIO) fails to respond within 30 days or provides misleading information, "
                    "file a First Appeal within 30 days under Section 19(1) of the RTI Act to the designated First Appellate Authority (FAA)."
                )
            elif "Information Technology" in p.act_or_document_name:
                procedural_steps.append(
                    "• **Cyber Crime Protocol**: Immediately dial the National Cyber Crime Helpline (1930) or lodge a report on cybercrime.gov.in, "
                    "and request an immediate freeze on the fraudulent recipient bank account / UPI transaction."
                )

        steps_text = "\n".join(procedural_steps) if procedural_steps else "• Review the statutory provisions and consult qualified legal counsel for representation."

        explanation = (
            f"### Situation Summary\n"
            f"Your scenario focuses on **{facts.legal_issue or 'constitutional and legal rights'}** "
            f"involving parties identified as *{', '.join(facts.actors or ['Citizen'])}*.\n\n"
            f"### Primary Applicable Legal Foundations\n"
            f"The primary provisions governing this situation are: **{prov_citations}**.\n\n"
            f"### Actionable Safeguards & Procedural Rights\n"
            f"{steps_text}\n\n"
            f"### Important Notice\n"
            f"This breakdown is generated for educational awareness and legal literacy based on verified Indian statutory texts. "
            f"For formal court filings or urgent criminal proceedings, consult an advocate registered with the State Bar Council."
        )

        return explanation
