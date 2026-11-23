import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.content import Question, get_lesson
from app.db import AsyncSession, get_session
from app.models import QuizAttempt

router = APIRouter(prefix="/api/quiz")


class QuizIn(BaseModel):
    answers: list[list[int]]  # chosen option indices, one list per question


def score_quiz(questions: list[Question], chosen: list[list[int]]) -> list[bool]:
    """A question is right only if the chosen set equals the answer set exactly."""
    return [sorted(set(c)) == sorted(q.answer) for q, c in zip(questions, chosen, strict=True)]


@router.post("/{track_id}/{slug}")
async def submit_quiz(track_id: str, slug: str, body: QuizIn, session: AsyncSession = Depends(get_session)):
    lesson = get_lesson(track_id, slug)
    if not lesson or not lesson.quiz:
        raise HTTPException(404, "No quiz for this lesson")
    if len(body.answers) != len(lesson.quiz):
        raise HTTPException(400, f"Expected {len(lesson.quiz)} answers")
    results = score_quiz(lesson.quiz, body.answers)
    score = sum(results)

    session.add(
        QuizAttempt(lesson_id=lesson.ref.id, score=score, total=len(results), answers_json=json.dumps(body.answers))
    )
    await session.commit()

    return {
        "score": score,
        "total": len(results),
        "results": [
            {"correct": ok, "answer": q.answer, "explain": q.explain} for q, ok in zip(lesson.quiz, results)
        ],
    }
