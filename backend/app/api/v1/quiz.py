from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/quiz", tags=["Constitutional Awareness Quiz"])


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_index: int
    explanation: str
    related_article: str


class QuizAnswerSubmission(BaseModel):
    question_id: int
    selected_option_index: int


class QuizAnswerResult(BaseModel):
    question_id: int
    is_correct: bool
    correct_index: int
    explanation: str
    related_article: str


SAMPLE_QUIZZES = [
    QuizQuestion(
        id=1,
        question="Which Article of the Constitution of India guarantees the Right to Protection of Life and Personal Liberty?",
        options=["Article 14", "Article 19", "Article 21", "Article 32"],
        correct_index=2,
        explanation="Article 21 declares that no person shall be deprived of life or personal liberty except according to procedure established by law (expanded in Puttaswamy & Maneka Gandhi cases).",
        related_article="Article 21"
    ),
    QuizQuestion(
        id=2,
        question="Under which Article can an Indian citizen approach the Supreme Court directly for the enforcement of Fundamental Rights?",
        options=["Article 226", "Article 32", "Article 136", "Article 142"],
        correct_index=1,
        explanation="Article 32 guarantees the Right to Constitutional Remedies via Writs (Habeas Corpus, Mandamus, etc.), referred to by Dr. B.R. Ambedkar as the 'heart and soul' of the Constitution.",
        related_article="Article 32"
    ),
    QuizQuestion(
        id=3,
        question="Within how many hours must an arrested individual be produced before the nearest Judicial Magistrate according to Article 22(2)?",
        options=["12 hours", "24 hours", "48 hours", "72 hours"],
        correct_index=1,
        explanation="Article 22(2) and Section 57 CrPC strictly mandate production of every arrested person before the nearest Magistrate within 24 hours (excluding transit time).",
        related_article="Article 22(2)"
    ),
    QuizQuestion(
        id=4,
        question="Which section mandates that a police officer issue a notice of appearance rather than an arrest for offences punishable up to 7 years?",
        options=["Section 41A CrPC", "Section 154 CrPC", "Section 100 CrPC", "Section 436 CrPC"],
        correct_index=0,
        explanation="Section 41A CrPC (now Sec 35 BNSS), as upheld in Arnesh Kumar v. State of Bihar, mandates notice of appearance for offences punishable with up to 7 years imprisonment.",
        related_article="Section 41A CrPC"
    ),
    QuizQuestion(
        id=5,
        question="Under the Right to Information (RTI) Act 2005, what is the statutory time limit for a Public Information Officer to respond?",
        options=["7 days", "15 days", "30 days (48 hrs if life/liberty)", "60 days"],
        correct_index=2,
        explanation="Section 7(1) of the RTI Act mandates information disposal within 30 days, or within 48 hours if concerning the life or liberty of any person.",
        related_article="Section 7 RTI Act"
    ),
    QuizQuestion(
        id=6,
        question="What writ is issued by the High Court or Supreme Court to secure the immediate release of a person in unlawful or illegal custody?",
        options=["Mandamus", "Habeas Corpus", "Certiorari", "Quo Warranto"],
        correct_index=1,
        explanation="Habeas Corpus (literally 'to have the body') is the primary constitutional writ against unlawful or arbitrary physical detention by state or private actors.",
        related_article="Article 32 / 226"
    )
]


@router.get("/questions", response_model=List[QuizQuestion])
async def get_quiz_questions():
    """
    Returns foundational civic & constitutional rights awareness quiz questions.
    """
    return SAMPLE_QUIZZES


@router.post("/submit", response_model=QuizAnswerResult)
async def submit_quiz_answer(payload: QuizAnswerSubmission):
    """
    Validates a submitted quiz answer and returns instant feedback with constitutional explanation.
    """
    question = next((q for q in SAMPLE_QUIZZES if q.id == payload.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Quiz question not found")

    is_correct = payload.selected_option_index == question.correct_index
    return QuizAnswerResult(
        question_id=question.id,
        is_correct=is_correct,
        correct_index=question.correct_index,
        explanation=question.explanation,
        related_article=question.related_article
    )
