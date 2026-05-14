import json
import os
import random
import re

from google import genai


FALLBACK_QUESTIONS = {
    "Mathematics": {
        3: [
            {
                "question": "Mia has 24 stickers. She gives 8 to her friend. How many stickers does Mia have left?",
                "options": ["12", "14", "16", "18"],
                "answer": "16",
                "explanation": "Subtract the stickers Mia gave away: 24 - 8 = 16.",
            },
            {
                "question": "Which fraction shows 1 out of 4 equal parts shaded?",
                "options": ["1/2", "1/3", "1/4", "4/1"],
                "answer": "1/4",
                "explanation": "One shaded part out of four equal parts is written as 1/4.",
            },
        ],
        5: [
            {
                "question": "Which number is equal to 4.7?",
                "options": ["47 tenths", "47 hundredths", "4 tenths and 7 ones", "407 tenths"],
                "answer": "47 tenths",
                "explanation": "4.7 means 4 ones and 7 tenths, which is the same as 47 tenths.",
            },
            {
                "question": "A rectangular box is 5 cm long, 3 cm wide, and 2 cm tall. What is its volume?",
                "options": ["10 cubic cm", "15 cubic cm", "30 cubic cm", "35 cubic cm"],
                "answer": "30 cubic cm",
                "explanation": "Volume is length x width x height, so 5 x 3 x 2 = 30 cubic cm.",
            },
            {
                "question": "A class read 125 pages on Monday and 148 pages on Tuesday. About how many pages did they read in all?",
                "options": ["About 200", "About 270", "About 400", "About 500"],
                "answer": "About 270",
                "explanation": "125 + 148 = 273, which is about 270.",
            },
        ],
    },
    "Science": {
        3: [
            {
                "question": "Which animal group has feathers and lays eggs?",
                "options": ["Birds", "Fish", "Mammals", "Insects"],
                "answer": "Birds",
                "explanation": "Birds have feathers, and most birds lay eggs.",
            },
            {
                "question": "What usually happens to a puddle on a sunny day?",
                "options": ["It freezes", "It evaporates", "It turns into soil", "It becomes a rock"],
                "answer": "It evaporates",
                "explanation": "The Sun warms the water, and it changes into water vapor.",
            },
        ],
        5: [
            {
                "question": "What role does a decomposer have in an ecosystem?",
                "options": ["It makes sunlight", "It breaks down dead plants and animals", "It hunts every animal", "It stops all plants from growing"],
                "answer": "It breaks down dead plants and animals",
                "explanation": "Decomposers return nutrients to the soil by breaking down dead matter.",
            },
            {
                "question": "A ball rolls farther on tile than on carpet. Which force is stronger on the carpet?",
                "options": ["Gravity", "Friction", "Magnetism", "Light"],
                "answer": "Friction",
                "explanation": "Carpet creates more friction, which slows the ball down.",
            },
        ],
    },
    "English": {
        3: [
            {
                "question": "Which word is an adjective in this sentence: The red kite flew high.",
                "options": ["red", "kite", "flew", "high"],
                "answer": "red",
                "explanation": "Red describes the kite, so it is an adjective.",
            },
            {
                "question": "Choose the sentence with correct capitalization.",
                "options": ["my dog is named spot.", "My dog is named Spot.", "my Dog is named spot.", "My dog is named spot."],
                "answer": "My dog is named Spot.",
                "explanation": "The first word and the name Spot both need capital letters.",
            },
        ],
        5: [
            {
                "question": "Which sentence uses a comma correctly?",
                "options": [
                    "After school, we went to the library.",
                    "After, school we went to the library.",
                    "After school we, went to the library.",
                    "After school we went, to the library.",
                ],
                "answer": "After school, we went to the library.",
                "explanation": "A comma can come after an opening phrase like 'After school.'",
            },
            {
                "question": "What is the best meaning of the word 'predict'?",
                "options": ["To explain what happened", "To guess what may happen next", "To copy a sentence", "To read out loud"],
                "answer": "To guess what may happen next",
                "explanation": "Predict means to use clues to tell what might happen next.",
            },
        ],
    },
    "History": {
        3: [
            {
                "question": "Why do communities make rules?",
                "options": ["To keep people safe", "To make maps", "To change the weather", "To grow food faster"],
                "answer": "To keep people safe",
                "explanation": "Rules help people work, play, and live together safely.",
            }
        ],
        5: [
            {
                "question": "Why are primary sources useful when learning history?",
                "options": ["They come from the time being studied", "They always tell the future", "They replace every map", "They are only fiction stories"],
                "answer": "They come from the time being studied",
                "explanation": "Primary sources are useful because they were made by people who saw or lived during an event.",
            },
            {
                "question": "Which action is an example of civic responsibility?",
                "options": ["Voting in an election", "Ignoring community rules", "Littering in a park", "Keeping all ideas secret"],
                "answer": "Voting in an election",
                "explanation": "Civic responsibility means helping your community, and voting is one example.",
            },
            {
                "question": "Why did trade routes help cities grow?",
                "options": ["They moved goods and ideas between places", "They stopped people from traveling", "They made farms disappear", "They kept cities isolated"],
                "answer": "They moved goods and ideas between places",
                "explanation": "Trade routes helped people exchange goods, ideas, and culture.",
            },
        ],
    },
    "Geography": {
        3: [
            {
                "question": "What tool helps people find directions and places?",
                "options": ["A map", "A thermometer", "A microscope", "A ruler"],
                "answer": "A map",
                "explanation": "A map shows where places are and can help with directions.",
            }
        ],
        5: [
            {
                "question": "Which map feature explains what symbols on a map mean?",
                "options": ["Map key", "Compass rose", "Scale bar", "Title"],
                "answer": "Map key",
                "explanation": "A map key, or legend, explains the symbols used on a map.",
            },
            {
                "question": "Which landform is a large, flat area higher than the land around it?",
                "options": ["Plateau", "Valley", "Island", "Peninsula"],
                "answer": "Plateau",
                "explanation": "A plateau is raised land with a mostly flat top.",
            },
            {
                "question": "Why do many cities grow near rivers or coasts?",
                "options": ["Water helps with travel, trade, and resources", "Water removes the need for roads", "Water makes every place cold", "Water stops all farming"],
                "answer": "Water helps with travel, trade, and resources",
                "explanation": "Rivers and coasts can support transportation, trade, food, and fresh water.",
            },
        ],
    },
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
- For Grade 3, use short concrete wording, familiar situations, and single-step reasoning.
- For Grade 5, use age-appropriate vocabulary and mild multi-step reasoning without middle-school concepts.
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

    return _fallback_questions(subject, topic, grade, count)


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


def _fallback_questions(subject: str, topic: str, grade: int, count: int) -> list[dict]:
    subject_bank = FALLBACK_QUESTIONS.get(subject, {})
    if subject_bank:
        target_grade = 3 if grade <= 3 else 5
        bank = subject_bank.get(target_grade) or subject_bank.get(5) or subject_bank.get(3)
        if bank:
            return random.choices(bank, k=count)
    return [
        {
            "question": f"Which answer best matches what you are learning about {topic}?",
            "options": ["A key word", "An example", "A main idea", "All of these"],
            "answer": "All of these",
            "explanation": f"Learning {topic} can include key words, examples, and main ideas.",
        }
        for _ in range(count)
    ]
