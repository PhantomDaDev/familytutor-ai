import json
import os
import random
import re

from google import genai


FALLBACK_QUESTIONS = {
    "Mathematics": [
        {
            "question": "What is 7 x 8?",
            "options": ["54", "56", "63", "48"],
            "answer": "56",
            "explanation": "7 x 8 = 56. You can think of it as 7 groups of 8.",
        },
        {
            "question": "What is 25% of 80?",
            "options": ["15", "20", "25", "30"],
            "answer": "20",
            "explanation": "25% means one quarter. One quarter of 80 is 20.",
        },
    ],
    "Science": [
        {
            "question": "What do plants need to make their own food?",
            "options": ["Moonlight and water", "Sunlight, water, and carbon dioxide", "Soil and oxygen", "Rain and wind"],
            "answer": "Sunlight, water, and carbon dioxide",
            "explanation": "Plants use photosynthesis with sunlight, water, and carbon dioxide.",
        },
    ],
    "English": [
        {
            "question": "Which sentence uses a comma correctly?",
            "options": [
                "I like cats, and dogs.",
                "She ran quickly, and jumped high.",
                "He ate breakfast, then left.",
                "They played football, and they won.",
            ],
            "answer": "They played football, and they won.",
            "explanation": "A comma before 'and' can join two complete sentences.",
        },
    ],
}


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def generate_questions(subject: str, topic: str, grade: int, count: int = 5, difficulty: int = 1) -> list[dict]:
    difficulty_label = {1: "easy", 2: "medium", 3: "hard"}.get(difficulty, "medium")
    prompt = f"""You are an expert educational quiz creator for school students.

Generate exactly {count} multiple-choice quiz questions for:
- Subject: {subject}
- Topic: {topic}
- Grade level: Grade {grade}
- Difficulty: {difficulty_label}

Return only a valid JSON array with this shape:
[
  {{
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A",
    "explanation": "Brief explanation."
  }}
]

Rules:
- All 4 options must be plausible.
- The answer must exactly match one option.
- Keep language appropriate for Grade {grade}.
- Explanations should be encouraging and educational.
"""

    client = _get_client()
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw = response.text.strip()
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
            questions = json.loads(raw)
            validated = []
            for question in questions:
                if all(key in question for key in ["question", "options", "answer", "explanation"]):
                    if question["answer"] in question["options"] and len(question["options"]) == 4:
                        validated.append(question)
            if validated:
                return validated[:count]
        except Exception:
            pass

    return _fallback_questions(subject, topic, count)


def generate_hint(question: str, topic: str, grade: int) -> str:
    client = _get_client()
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Give a short hint for this Grade {grade} {topic} question without revealing the answer: {question}",
            )
            return response.text.strip()
        except Exception:
            pass

    return f"Think about the key idea from {topic}, then eliminate answers that do not fit."


def generate_encouragement(correct: bool, child_name: str, score: int, total: int) -> str:
    client = _get_client()
    if client:
        try:
            mood = "great" if total and score / total >= 0.7 else "keep trying"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Write a short, warm encouragement for {child_name}, who scored {score}/{total}. Mood: {mood}. No emoji.",
            )
            return response.text.strip()
        except Exception:
            pass

    if correct:
        return f"Well done, {child_name}. You are building real momentum."
    return f"Good effort, {child_name}. A little practice will make this feel easier."


def _fallback_questions(subject: str, topic: str, count: int) -> list[dict]:
    bank = FALLBACK_QUESTIONS.get(subject, [])
    if bank:
        return random.choices(bank, k=count)
    return [
        {
            "question": f"What is an important concept in {topic}?",
            "options": ["Definition", "Example", "Process", "All of these"],
            "answer": "All of these",
            "explanation": f"Understanding {topic} often includes definitions, examples, and processes.",
        }
        for _ in range(count)
    ]
