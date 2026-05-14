import html

import streamlit as st

from core.database import (
    get_all_topics,
    get_child,
    get_child_subjects,
    get_due_topics,
    get_streak,
    get_subject_stats,
)


AVATAR_EMOJI = {
    "star": "&#9733;",
    "rocket": "&#128640;",
    "dragon": "&#128009;",
    "unicorn": "&#129412;",
    "robot": "&#129302;",
    "owl": "&#129417;",
    "lion": "&#129409;",
    "fox": "&#129418;",
}

SUBJECT_ICONS = {
    "Mathematics": "&#128208;",
    "Science": "&#128300;",
    "English": "&#128214;",
    "History": "&#127963;",
    "Geography": "&#127757;",
}


def render():
    child_id = st.session_state.get("active_child_id")
    if not child_id:
        st.session_state.page = "home"
        st.rerun()

    child = get_child(child_id)
    if not child:
        st.session_state.page = "home"
        st.rerun()

    streak = get_streak(child_id)
    subjects = get_child_subjects(child_id)
    stats = get_subject_stats(child_id)
    stats_map = {item["subject"]: item for item in stats}
    avatar = AVATAR_EMOJI.get(child["avatar"], "&#9733;")
    avatar_markup = f'<div class="dash-avatar">{avatar}</div>' if child["avatar"] else ""
    header_markup = "\n".join(
        [
            '<div class="dashboard-header">',
            avatar_markup,
            '<div class="dash-info">',
            f'<h1>{html.escape(child["name"])}</h1>',
            f'<span class="grade-badge">Grade {child["grade"]}</span>',
            '</div>',
            '<div class="dash-streak-block">',
            f'<div class="streak-number">{streak.get("current_streak", 0)}</div>',
            '<div class="streak-label">day streak</div>',
            '</div>',
            '</div>',
        ]
    )

    st.markdown(
        header_markup,
        unsafe_allow_html=True,
    )

    total_q = sum(item["total_q"] or 0 for item in stats)
    total_correct = sum(item["total_correct"] or 0 for item in stats)
    overall_accuracy = round(total_correct / total_q * 100) if total_q else 0
    total_sessions = sum(item["sessions"] or 0 for item in stats)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _stat_card(total_q, "Questions answered")
    with c2:
        _stat_card(f"{overall_accuracy}%", "Overall accuracy")
    with c3:
        _stat_card(total_sessions, "Sessions completed")
    with c4:
        _stat_card(streak.get("total_stars", 0), "Stars earned")

    st.markdown("<h3>Choose a subject</h3>", unsafe_allow_html=True)

    cols = st.columns(max(1, len(subjects)))
    for index, subject in enumerate(subjects):
        with cols[index]:
            item = stats_map.get(subject, {})
            q_count = item.get("total_q") or 0
            correct = item.get("total_correct") or 0
            accuracy = round(correct / q_count * 100) if q_count else 0
            icon = SUBJECT_ICONS.get(subject, "&#128218;")
            due = len(get_due_topics(child_id, subject))
            due_badge = (
                f'<span class="due-badge">{due} due</span>'
                if due
                else '<span class="due-badge zero">up to date</span>'
            )

            st.markdown(
                f"""
                <div class="subject-card">
                    <div class="subj-icon">{icon}</div>
                    <div class="subj-name">{html.escape(subject)}</div>
                    <div class="subj-acc">{accuracy}% accuracy</div>
                    <div class="subj-meta">{q_count} questions | {due_badge}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(f"Start {subject}", key=f"start_{subject}", use_container_width=True):
                st.session_state.selected_subject = subject
                st.session_state.page = "quiz_setup"
                st.rerun()

    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("View progress report", use_container_width=True):
            st.session_state.page = "report"
            st.rerun()
    with col_b:
        if st.button("Switch learner", use_container_width=True):
            st.session_state.active_child_id = None
            st.session_state.page = "home"
            st.rerun()
    with col_c:
        if st.button("Add learner", use_container_width=True):
            st.session_state.page = "add_child"
            st.rerun()


def _stat_card(value, label):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-val">{value}</div>
            <div class="stat-lbl">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
