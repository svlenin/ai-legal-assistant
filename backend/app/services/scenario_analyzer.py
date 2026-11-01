"""
Scenario Analyzer Service.
Performs natural language parsing, structured fact extraction,
legal domain classification, and urgency/risk assessment.
"""
import re
from typing import List, Tuple
from app.schemas.scenario import ExtractedFacts, ScenarioAnalyzeResponse


class ScenarioAnalyzerService:
    # Rule-based entity and domain matching patterns for deterministic, explainable extraction
    ACTOR_PATTERNS = [
        ("Police Officer / Law Enforcement", r"\b(police|cop|constable|si|inspector|station|chowki|investigating officer|io)\b"),
        ("Government / Public Official", r"\b(officer|collector|tehsildar|bdo|government official|corporation|municipality|public authority|pio)\b"),
        ("Employer / Organization", r"\b(boss|manager|company|employer|hr|workplace|office|firm)\b"),
        ("Merchant / Seller / Service Provider", r"\b(seller|shopkeeper|merchant|vendor|dealer|store|e-commerce|flipkart|amazon|builder)\b"),
        ("Educational Institution / College", r"\b(school|college|principal|university|teacher|faculty|administration)\b"),
        ("Landlord / Neighbor", r"\b(landlord|owner|tenant|neighbor|flat owner)\b"),
        ("Bank / Financial Entity", r"\b(bank|manager|loan agent|recovery agent|fintech|branch)\b"),
        ("Online Impersonator / Scammer", r"\b(scammer|hacker|phishing|caller|unknown number|impersonator|fraudster)\b"),
        ("Aggrieved Citizen / Complainant", r"\b(i|me|my|we|our|citizen|applicant|consumer|victim|student|employee)\b"),
    ]

    DOMAIN_MAPPINGS = [
        ("Criminal Procedure & Police Powers", r"\b(arrest|fir|police station|custody|detained|lockup|bail|warrant|interrogate|torture|handcuff)\b"),
        ("Fundamental Rights", r"\b(fundamental right|article 14|article 19|article 21|article 32|equality|discrimination|speech|protest|expression|privacy|life and liberty|dignity)\b"),
        ("Constitutional Remedies & Writs", r"\b(writ|habeas corpus|mandamus|certiorari|high court|supreme court|illegal custody|quash order)\b"),
        ("Consumer Rights & Commerce", r"\b(defect|defective|warranty|refund|expired|consumer forum|overcharged|false advertisement|broken product|e-commerce)\b"),
        ("Administrative Transparency & RTI", r"\b(rti|right to information|pio|public information|government record|information request|appeals)\b"),
        ("Cyber & Digital Rights", r"\b(cyber|hacked|phishing|otp|upi fraud|online fraud|identity theft|leak|whatsapp|impersonation|social media)\b"),
        ("Education & Child Rights", r"\b(school admission|rte|right to education|child|student fee|dropout|expelled)\b")
    ]

    URGENCY_TRIGGERS = [
        r"\b(arrest(ed)?|detain(ed)?|handcuff(ed)?|assault|beaten|torture|custody|locked up|threat|violence|suicide|kidnap)\b"
    ]

    @classmethod
    async def analyze_scenario(cls, raw_query: str, language: str = "en") -> ScenarioAnalyzeResponse:
        query_text = raw_query.strip()
        lower_query = query_text.lower()

        # 1. Extract Actors
        detected_actors = []
        for actor_label, pattern in cls.ACTOR_PATTERNS:
            if re.search(pattern, lower_query):
                detected_actors.append(actor_label)
        if not detected_actors:
            detected_actors.append("Complainant / Aggrieved Individual")

        # 2. Extract Events / Timeline
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', query_text) if len(s.strip()) > 5]
        key_events = sentences[:4] if sentences else [query_text]

        # 3. Location / Jurisdiction hints
        location = "India (General Territorial Jurisdiction)"
        loc_match = re.search(r'\b(in|at|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\b', query_text)
        if loc_match:
            location = loc_match.group(2)

        # 4. Identify Domains
        detected_domains = []
        for domain_name, pattern in cls.DOMAIN_MAPPINGS:
            if re.search(pattern, lower_query):
                detected_domains.append(domain_name)
        if not detected_domains:
            detected_domains.append("Fundamental Rights & General Constitutional Law")

        # 5. Core Legal Issue classification
        legal_issue = cls._classify_legal_issue(lower_query)

        # 6. Action Type
        action_type = "Constitutional / Statutory Grievance"
        if any(d in detected_domains for d in ["Criminal Procedure & Police Powers", "Cyber & Digital Rights"]):
            action_type = "Criminal & Procedural / Police Inquiry"
        elif "Consumer Rights & Commerce" in detected_domains:
            action_type = "Consumer Dispute / Civil Redressal"

        extracted = ExtractedFacts(
            actors=detected_actors,
            key_events=key_events,
            location=location,
            legal_issue=legal_issue,
            action_type=action_type
        )

        # 7. Urgency & Risk Detection
        risk_level = "STANDARD"
        urgency_advisory = None
        for trigger_pat in cls.URGENCY_TRIGGERS:
            if re.search(trigger_pat, lower_query):
                risk_level = "URGENT"
                urgency_advisory = (
                    "HIGH URGENCY ALERT: This scenario indicates potential physical detention, custodial coercion, "
                    "or imminent deprivation of liberty. You are entitled to immediate legal representation under Article 22(1). "
                    "Emergency Contact: National Emergency Helpline (112), Legal Aid Helpline (15100 - NALSA), "
                    "or an advocate before the nearest Judicial Magistrate."
                )
                break

        # 8. Missing Information & Follow-Up Questions
        clarification_questions = cls._generate_clarifications(lower_query, detected_domains)

        return ScenarioAnalyzeResponse(
            scenario_id=None,
            extracted_facts=extracted,
            identified_domains=detected_domains,
            risk_level=risk_level,
            urgency_advisory=urgency_advisory,
            clarification_questions=clarification_questions
        )

    @staticmethod
    def _classify_legal_issue(query: str) -> str:
        if "arrest" in query or "custody" in query or "detain" in query:
            return "Arrest, Custodial Rights, and Safeguards under Procedure Established by Law"
        if "fir" in query or "refuse to register" in query or "police report" in query:
            return "Registration of First Information Report (Mandatory FIR) and Police Duty"
        if "speech" in query or "protest" in query or "post" in query or "video" in query:
            return "Freedom of Speech, Peaceful Expression, and Reasonable Restrictions"
        if "defective" in query or "refund" in query or "warranty" in query or "fraud" in query:
            return "Deficiency of Consumer Services, Unfair Trade Practices, and Compensation Redressal"
        if "rti" in query or "information" in query or "officer not replying" in query:
            return "Citizen's Right to Information and Public Authority Transparency"
        if "upi" in query or "cyber" in query or "hacked" in query or "impersonat" in query:
            return "Cyber Fraud, Digital Identity Theft, and Electronic Impersonation"
        if "equality" in query or "discrimina" in query:
            return "Protection against Arbitrary State Discrimination and Equality before Law"
        return "Assessment of Constitutional Fundamental Rights and Statutory Remedies"

    @staticmethod
    def _generate_clarifications(query: str, domains: List[str]) -> List[str]:
        questions = []
        if "Criminal Procedure & Police Powers" in domains:
            questions.append("Was any written notice (such as Section 41A notice) or formal arrest memo provided by the police?")
            questions.append("Has the individual been produced before a Judicial Magistrate within 24 hours?")
        elif "Consumer Rights & Commerce" in domains:
            questions.append("Do you possess valid proofs of purchase, invoice receipts, or written communication with the seller?")
            questions.append("Was a formal written grievance or legal notice sent to the company?")
        elif "Administrative Transparency & RTI" in domains:
            questions.append("Has a formal Form A RTI application with prescribed fee been submitted to the designated Public Information Officer (PIO)?")
            questions.append("Have more than 30 days elapsed since the official submission date?")
        elif "Cyber & Digital Rights" in domains:
            questions.append("Have you registered an immediate complaint on the National Cyber Crime Reporting Portal (cybercrime.gov.in / 1930)?")
            questions.append("Have you preserved transaction IDs, screenshots, and bank communication records?")
        else:
            questions.append("Did this action involve a public/government authority or private individual?")
            questions.append("Are there any written orders, rejection notices, or communications available?")
        return questions
