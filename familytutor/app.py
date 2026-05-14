import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from core.database import init_db


st.set_page_config(
    page_title="FamilyTutor AI",
    page_icon="FT",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def seed_demo_data():
    from core.database import (
        create_child,
        create_session,
        end_session,
        get_all_children,
        save_answer,
        update_streak,
    )
    import random

    normalize_demo_children()

    if get_all_children():
        return

    child1 = create_child("Kid 1", 3, "", ["Mathematics", "Science", "English"])
    child2 = create_child("Kid 2", 5, "", ["Mathematics", "History", "Geography"])

    subjects = {
        child1: [("Mathematics", "Fractions & Decimals"), ("Science", "Ecosystems"), ("English", "Grammar")],
        child2: [("Mathematics", "Algebra"), ("History", "Ancient Civilizations"), ("Geography", "Climate Zones")],
    }

    sample_questions = [
        ("What is 3/4 as a decimal?", "0.75", "0.75", True),
        ("What is 1/2 + 1/4?", "3/4", "1/2", False),
        ("What do producers make in an ecosystem?", "Food or energy", "Food or energy", True),
        ("Which sentence is grammatically correct?", "She runs fast.", "She runs fast.", True),
        ("What is x if 2x = 10?", "5", "5", True),
        ("Who built the pyramids?", "Ancient Egyptians", "Romans", False),
    ]

    for child_id, subject_topic_pairs in subjects.items():
        for _ in range(12):
            subject, topic = random.choice(subject_topic_pairs)
            session_id = create_session(child_id, subject, topic)
            total = random.randint(4, 8)
            correct = random.randint(2, total)
            for _ in range(total):
                question, correct_answer, user_answer, is_correct = random.choice(sample_questions)
                save_answer(session_id, question, correct_answer, user_answer, is_correct)
            end_session(session_id, total, correct)
        update_streak(child_id, stars_earned=random.randint(3, 8))


def normalize_demo_children():
    from core.database import get_conn

    conn = get_conn()
    conn.execute(
        "UPDATE children SET name=?, grade=?, avatar=? WHERE name IN (?, ?)",
        ("Kid 1", 3, "", "Layla", "Kid 1"),
    )
    conn.execute(
        "UPDATE children SET name=?, grade=?, avatar=? WHERE name IN (?, ?)",
        ("Kid 2", 5, "", "Omar", "Kid 2"),
    )
    conn.commit()
    conn.close()


STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #101117;
    --surface: #1b1d27;
    --surface2: #242735;
    --accent: #6f8cff;
    --accent2: #ffb84d;
    --accent3: #42d9a3;
    --accent4: #ff6b8a;
    --text: #f7f8fb;
    --muted: #aeb4c5;
    --border: rgba(255,255,255,0.1);
    --radius: 12px;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Nunito', sans-serif;
}

[data-testid="stSidebar"] { background: var(--surface) !important; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--text) !important; letter-spacing: 0; }

.page-header { text-align: center; padding: 2rem 0 1.5rem; }
.page-header h1 { font-size: 2.4rem; font-weight: 800; margin: 0; color: var(--text) !important; }
.page-header .subtitle { color: var(--muted); margin-top: .4rem; font-size: 1.05rem; }

.profile-card, .stat-card, .subject-card, .question-card, .config-preview, .results-header, .insight-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
}

.profile-card { padding: 1.5rem 1rem; text-align: center; margin-bottom: .75rem; }
.profile-avatar { font-size: 2.5rem; margin-bottom: .5rem; }
.profile-name { font-size: 1.3rem; font-weight: 800; color: var(--text); }
.profile-grade { color: var(--muted); font-size: .9rem; margin-bottom: .75rem; }
.profile-stats { display: flex; flex-wrap: wrap; gap: .4rem; justify-content: center; }
.stat-pill { background: var(--surface2); border-radius: 999px; padding: .2rem .7rem; font-size: .8rem; color: var(--muted); }

.stat-card { padding: 1.1rem; text-align: center; margin-bottom: .5rem; }
.stat-card.accent { border-color: var(--accent); }
.stat-val { font-size: 1.65rem; font-weight: 800; color: var(--accent); font-family: 'Space Grotesk', sans-serif; }
.stat-lbl { font-size: .85rem; color: var(--muted); margin-top: .2rem; }

.dashboard-header {
    display: flex; align-items: center; gap: 1.25rem;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.4rem 1.6rem; margin-bottom: 1.5rem;
}
.dash-avatar { font-size: 2.7rem; }
.dash-info h1 { font-size: 1.8rem; margin: 0; }
.grade-badge { background: var(--accent); color: #080a10; border-radius: 999px; padding: .2rem .8rem; font-size: .85rem; font-weight: 800; }
.dash-streak-block { margin-left: auto; text-align: center; }
.streak-number { font-size: 2.2rem; font-weight: 900; color: var(--accent2); font-family: 'Space Grotesk', sans-serif; }
.streak-label { font-size: .9rem; color: var(--muted); }

.subject-card { padding: 1.2rem 1rem; text-align: center; margin-bottom: .5rem; }
.subj-icon { font-size: 2rem; margin-bottom: .5rem; }
.subj-name { font-weight: 800; font-size: 1.1rem; color: var(--text); }
.subj-acc { color: var(--accent3); font-size: .9rem; margin: .3rem 0; }
.subj-meta { color: var(--muted); font-size: .8rem; }
.due-badge { background: rgba(255,184,77,.15); color: var(--accent2); border-radius: 999px; padding: .15rem .6rem; font-size: .78rem; font-weight: 800; }
.due-badge.zero { background: rgba(66,217,163,.1); color: var(--accent3); }

.topic-row {
    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
    padding: .8rem 1.1rem; margin-bottom: .5rem;
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.topic-row.due { border-color: var(--accent2); }
.topic-name { font-weight: 800; color: var(--text); }
.leitner-box, .topic-meta { font-size: .8rem; color: var(--muted); }
.section-label { font-size: .85rem; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: .75rem; }

.config-preview { padding: 1.4rem; margin: 1.5rem 0; }
.config-item { display: flex; justify-content: space-between; gap: 1rem; padding: .5rem 0; border-bottom: 1px solid var(--border); }
.config-item:last-child { border: none; }
.config-item span { color: var(--muted); }
.config-item strong { color: var(--text); }

.quiz-progress-wrap { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: .5rem; }
.quiz-progress-label { font-weight: 800; color: var(--text); }
.quiz-subject-tag { background: var(--surface2); color: var(--muted); border-radius: 999px; padding: .2rem .8rem; font-size: .85rem; }
.question-card { padding: 1.7rem 1.4rem; margin: 1rem 0; }
.question-number { color: var(--accent); font-weight: 800; font-size: .9rem; margin-bottom: .5rem; font-family: 'Space Grotesk', sans-serif; }
.question-text { font-size: 1.2rem; font-weight: 800; color: var(--text); line-height: 1.5; }

.answer-btn { padding: .9rem 1.2rem; border-radius: 10px; margin-bottom: .5rem; font-size: 1rem; font-weight: 700; border: 2px solid transparent; }
.answer-btn.correct-answer { background: rgba(66,217,163,.12); border-color: var(--accent3); color: var(--accent3); }
.answer-btn.wrong-answer { background: rgba(255,107,138,.12); border-color: var(--accent4); color: var(--accent4); }
.answer-btn.neutral-answer { background: var(--surface2); color: var(--muted); }
.feedback { padding: 1rem 1.2rem; border-radius: 10px; margin-top: .75rem; font-size: .95rem; line-height: 1.6; }
.feedback.correct { background: rgba(66,217,163,.1); border: 1px solid var(--accent3); color: var(--accent3); }
.feedback.wrong { background: rgba(255,107,138,.1); border: 1px solid var(--accent4); color: #ffd1dc; }

.results-header { text-align: center; padding: 2.3rem; margin-bottom: 1.5rem; }
.results-emoji { font-size: 3.2rem; margin-bottom: .5rem; }
.results-title { font-size: 2rem; font-weight: 800; color: var(--text); font-family: 'Space Grotesk', sans-serif; }
.results-score { font-size: 1.1rem; color: var(--muted); margin: .5rem 0; }
.results-pct { font-size: 3.3rem; font-weight: 900; color: var(--accent); font-family: 'Space Grotesk', sans-serif; }
.results-message { color: var(--muted); margin: 1rem 0; font-style: italic; }
.stars-earned { font-size: 1.3rem; margin-top: .5rem; }

.insight-box { padding: 1rem 1.2rem; margin-bottom: 1rem; }
.insight-box.strong { border-color: var(--accent3); }
.insight-box.weak { border-color: var(--accent2); }
.insight-title { font-weight: 800; margin-bottom: .5rem; color: var(--text); }
.session-row { display: flex; justify-content: space-between; align-items: center; gap: .75rem; background: var(--surface); border-radius: 10px; padding: .7rem 1rem; margin-bottom: .4rem; border: 1px solid var(--border); }
.session-subj { font-weight: 800; color: var(--accent); min-width: 100px; }
.session-topic { color: var(--text); flex: 1; }
.session-score { color: var(--accent3); font-weight: 800; }
.session-date { color: var(--muted); font-size: .85rem; min-width: 80px; text-align: right; }

.empty-state { text-align: center; padding: 4rem 2rem; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-text { font-size: 1.5rem; font-weight: 800; color: var(--text); }
.empty-sub { color: var(--muted); margin-top: .5rem; }

[data-testid="stButton"] button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
}
[data-testid="stButton"] button:hover {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #080a10 !important;
}
[data-testid="stProgressBar"] > div { background: var(--surface2) !important; border-radius: 999px; }
[data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, var(--accent), var(--accent3)) !important; border-radius: 999px; }
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
"""


def main():
    init_db()
    seed_demo_data()
    st.markdown(STYLES, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "home"

    routes = {
        "home": "pages.home",
        "add_child": "pages.add_child",
        "dashboard": "pages.dashboard",
        "quiz_setup": "pages.quiz_setup",
        "quiz_config": "pages.quiz_config",
        "quiz": "pages.quiz",
        "report": "pages.report",
    }

    module_name = routes.get(st.session_state.page)
    if not module_name:
        st.session_state.page = "home"
        st.rerun()

    module = __import__(module_name, fromlist=["render"])
    module.render()


if __name__ == "__main__":
    main()
