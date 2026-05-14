import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "familytutor.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS children (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade INTEGER NOT NULL,
        avatar TEXT DEFAULT 'star',
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS leitner_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        box INTEGER DEFAULT 1,
        next_review TEXT DEFAULT (datetime('now')),
        correct_streak INTEGER DEFAULT 0,
        FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        started_at TEXT DEFAULT (datetime('now')),
        ended_at TEXT,
        total_questions INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        user_answer TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        explanation TEXT,
        answered_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS streaks (
        child_id INTEGER PRIMARY KEY,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        last_session_date TEXT,
        total_stars INTEGER DEFAULT 0,
        FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

# ── Children ──────────────────────────────────────────────
def create_child(name, grade, avatar="star", subjects=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO children (name, grade, avatar) VALUES (?,?,?)", (name, grade, avatar))
    child_id = c.lastrowid
    if subjects:
        for s in subjects:
            c.execute("INSERT INTO subjects (child_id, name) VALUES (?,?)", (child_id, s))
            for topic in get_default_topics(s, grade):
                c.execute(
                    "INSERT INTO leitner_topics (child_id, subject, topic) VALUES (?,?,?)",
                    (child_id, s, topic)
                )
    c.execute("INSERT INTO streaks (child_id) VALUES (?)", (child_id,))
    conn.commit()
    conn.close()
    return child_id

def get_all_children():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM children ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_child(child_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_child_subjects(child_id):
    conn = get_conn()
    rows = conn.execute("SELECT name FROM subjects WHERE child_id=?", (child_id,)).fetchall()
    conn.close()
    return [r["name"] for r in rows]

def delete_child(child_id):
    conn = get_conn()
    conn.execute("DELETE FROM children WHERE id=?", (child_id,))
    conn.commit()
    conn.close()

# ── Leitner / Topics ──────────────────────────────────────
def get_due_topics(child_id, subject):
    now = datetime.now().isoformat()
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM leitner_topics WHERE child_id=? AND subject=? AND next_review<=? ORDER BY box ASC",
        (child_id, subject, now)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_topics(child_id, subject):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM leitner_topics WHERE child_id=? AND subject=?",
        (child_id, subject)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_topic_leitner(topic_id, correct):
    from datetime import timedelta
    conn = get_conn()
    row = conn.execute("SELECT * FROM leitner_topics WHERE id=?", (topic_id,)).fetchone()
    if not row:
        conn.close()
        return
    box = row["box"]
    streak = row["correct_streak"]
    if correct:
        streak += 1
        box = min(box + 1, 5)
    else:
        streak = 0
        box = max(box - 1, 1)
    intervals = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}
    next_review = (datetime.now() + timedelta(days=intervals[box])).isoformat()
    conn.execute(
        "UPDATE leitner_topics SET box=?, correct_streak=?, next_review=? WHERE id=?",
        (box, streak, next_review, topic_id)
    )
    conn.commit()
    conn.close()

# ── Sessions ──────────────────────────────────────────────
def create_session(child_id, subject, topic):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO sessions (child_id, subject, topic) VALUES (?,?,?)", (child_id, subject, topic))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid

def end_session(session_id, total, correct):
    conn = get_conn()
    conn.execute(
        "UPDATE sessions SET ended_at=datetime('now'), total_questions=?, correct=? WHERE id=?",
        (total, correct, session_id)
    )
    conn.commit()
    conn.close()

def save_answer(session_id, question, correct_answer, user_answer, is_correct, explanation=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO answers (session_id, question, correct_answer, user_answer, is_correct, explanation) VALUES (?,?,?,?,?,?)",
        (session_id, question, correct_answer, user_answer, int(is_correct), explanation)
    )
    conn.commit()
    conn.close()

def get_recent_sessions(child_id, limit=10):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sessions WHERE child_id=? AND ended_at IS NOT NULL ORDER BY started_at DESC LIMIT ?",
        (child_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_subject_stats(child_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT subject,
               COUNT(*) as sessions,
               SUM(total_questions) as total_q,
               SUM(correct) as total_correct
        FROM sessions
        WHERE child_id=? AND ended_at IS NOT NULL
        GROUP BY subject
    """, (child_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_topic_accuracy(child_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.topic, s.subject,
               SUM(s.total_questions) as total_q,
               SUM(s.correct) as total_correct
        FROM sessions s
        WHERE s.child_id=? AND s.ended_at IS NOT NULL AND s.total_questions > 0
        GROUP BY s.subject, s.topic
    """, (child_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_daily_activity(child_id, days=14):
    conn = get_conn()
    rows = conn.execute("""
        SELECT DATE(started_at) as day,
               COUNT(*) as sessions,
               SUM(correct) as correct,
               SUM(total_questions) as total
        FROM sessions
        WHERE child_id=? AND ended_at IS NOT NULL
              AND started_at >= datetime('now', ? || ' days')
        GROUP BY day ORDER BY day
    """, (child_id, f"-{days}")).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Streaks ───────────────────────────────────────────────
def update_streak(child_id, stars_earned=1):
    from datetime import date, timedelta
    conn = get_conn()
    row = conn.execute("SELECT * FROM streaks WHERE child_id=?", (child_id,)).fetchone()
    today = date.today().isoformat()
    if row:
        last = row["last_session_date"]
        streak = row["current_streak"]
        longest = row["longest_streak"]
        total_stars = row["total_stars"] + stars_earned
        if last == today:
            pass
        elif last == (date.today() - timedelta(days=1)).isoformat():
            streak += 1
        else:
            streak = 1
        longest = max(longest, streak)
        conn.execute(
            "UPDATE streaks SET current_streak=?, longest_streak=?, last_session_date=?, total_stars=? WHERE child_id=?",
            (streak, longest, today, total_stars, child_id)
        )
    conn.commit()
    conn.close()

def get_streak(child_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM streaks WHERE child_id=?", (child_id,)).fetchone()
    conn.close()
    return dict(row) if row else {"current_streak": 0, "longest_streak": 0, "total_stars": 0}

# ── Defaults ──────────────────────────────────────────────
TOPIC_BANK = {
    "Mathematics": {
        range(1, 4): ["Addition & Subtraction", "Multiplication", "Division", "Fractions Basics", "Shapes & Geometry"],
        range(5, 6): ["Decimals & Place Value", "Volume", "Estimation", "Multi-Step Word Problems"],
        range(4, 7): ["Fractions & Decimals", "Percentages", "Algebra Intro", "Geometry", "Word Problems"],
        range(7, 13): ["Algebra", "Geometry", "Statistics", "Trigonometry", "Calculus Intro"],
    },
    "Science": {
        range(1, 4): ["Plants & Animals", "Weather", "Matter & Energy", "Human Body Basics"],
        range(5, 6): ["Food Webs", "Forces & Friction", "Earth Systems", "Matter Changes"],
        range(4, 7): ["Ecosystems", "Forces & Motion", "States of Matter", "Earth & Space"],
        range(7, 13): ["Biology", "Chemistry", "Physics", "Environmental Science"],
    },
    "English": {
        range(1, 4): ["Reading Comprehension", "Spelling", "Grammar Basics", "Creative Writing"],
        range(5, 6): ["Main Idea & Evidence", "Vocabulary in Context", "Commas & Clauses", "Opinion Writing"],
        range(4, 7): ["Grammar", "Vocabulary", "Essay Writing", "Poetry"],
        range(7, 13): ["Literature Analysis", "Advanced Grammar", "Persuasive Writing", "Research Skills"],
    },
    "History": {
        range(1, 4): ["Community & Family", "National Symbols", "Famous People"],
        range(5, 6): ["Primary Sources", "Civics & Government", "Trade Routes", "Timelines"],
        range(4, 7): ["Ancient Civilizations", "World Explorers", "Local History"],
        range(7, 13): ["World Wars", "Modern History", "Geography & Politics", "Economics"],
    },
    "Geography": {
        range(1, 4): ["Continents & Oceans", "Maps & Directions", "Countries & Capitals"],
        range(5, 6): ["Map Skills", "Landforms & Waterways", "Regions & Resources", "Latitude & Longitude"],
        range(4, 7): ["Climate Zones", "Natural Disasters", "World Cultures"],
        range(7, 13): ["Physical Geography", "Human Geography", "Environmental Issues"],
    },
}

def get_default_topics(subject, grade):
    bank = TOPIC_BANK.get(subject, {})
    for grade_range, topics in bank.items():
        if grade in grade_range:
            return topics
    return ["General Knowledge"]

AVAILABLE_SUBJECTS = list(TOPIC_BANK.keys())
AVATARS = ["star", "rocket", "dragon", "unicorn", "robot", "owl", "lion", "fox"]
