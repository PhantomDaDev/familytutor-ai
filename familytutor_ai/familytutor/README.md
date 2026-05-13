# FamilyTutor AI 🎓

An intelligent home tutoring app for families — powered by Python, Streamlit, and the Gemini API.

## Features

- **Multi-child profiles** — individual profiles for each child with avatars, grade, and subjects
- **AI-generated questions** — fresh, grade-appropriate questions via Gemini
- **Spaced repetition** — Leitner box algorithm schedules reviews at optimal intervals
- **Adaptive difficulty** — Easy / Medium / Hard modes
- **Gamification** — streaks, stars, and instant feedback
- **Progress reports** — charts for accuracy by subject, daily activity, and topic breakdown
- **Hint system** — AI-generated hints without giving away answers

## Setup

```bash
# 1. Clone / unzip the project
cd familytutor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Gemini API key
export GEMINI_API_KEY="your-key-here"
# Windows: set GEMINI_API_KEY=your-key-here

# 4. Run
streamlit run app.py
```

The app will open at http://localhost:8501

Two demo profiles (Layla and Omar) are seeded automatically on first run.

## Project Structure

```
familytutor/
├── app.py              # Main entry point, routing, CSS
├── requirements.txt
├── core/
│   ├── database.py     # SQLite models, Leitner logic, all DB ops
│   ├── ai_engine.py    # Gemini API — question/hint/encouragement generation
│   └── reports.py      # Matplotlib chart generation
└── pages/
    ├── home.py         # Profile selection
    ├── add_child.py    # New profile form
    ├── dashboard.py    # Subject selection + stats
    ├── quiz_setup.py   # Topic picker with Leitner status
    ├── quiz_config.py  # Difficulty + question count
    ├── quiz.py         # Quiz session + results
    └── report.py       # Progress report with charts
```

## How Leitner Spaced Repetition Works

Topics are placed in 5 boxes with increasing review intervals:
- Box 1: review every 1 day
- Box 2: every 2 days  
- Box 3: every 4 days
- Box 4: every 8 days
- Box 5: every 16 days

Score ≥70% on a topic → moves up one box (reviewed less often)
Score <70% → moves down one box (reviewed more often)

## Tech Stack

- **Python 3.11+**
- **Streamlit** — UI framework
- **SQLite** — local database (zero config)
- **Gemini API** — question generation, hints, encouragement
- **Matplotlib** — progress charts
- **Numpy** — chart calculations
