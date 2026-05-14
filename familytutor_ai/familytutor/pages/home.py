import html

import streamlit as st

from core.database import delete_child, get_all_children, get_streak, get_subject_stats


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


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>Who's learning today?</h1>
            <p class="subtitle">Pick a learner profile to start a tutoring session.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    children = get_all_children()
    if not children:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">&#127793;</div>
                <div class="empty-text">No learners yet</div>
                <div class="empty-sub">Add your first child profile to get started.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        cols = st.columns(3)
        for index, child in enumerate(children):
            with cols[index % 3]:
                streak = get_streak(child["id"])
                stats = get_subject_stats(child["id"])
                total_q = sum(item["total_q"] or 0 for item in stats)
                total_correct = sum(item["total_correct"] or 0 for item in stats)
                accuracy = round(total_correct / total_q * 100) if total_q else 0
                avatar = AVATAR_EMOJI.get(child["avatar"], "&#9733;")
                avatar_markup = f'<div class="profile-avatar">{avatar}</div>' if child["avatar"] else ""
                profile_markup = "\n".join(
                    [
                        '<div class="profile-card">',
                        avatar_markup,
                        f'<div class="profile-name">{html.escape(child["name"])}</div>',
                        f'<div class="profile-grade">Grade {child["grade"]}</div>',
                        '<div class="profile-stats">',
                        f'<span class="stat-pill">{streak.get("current_streak", 0)} day streak</span>',
                        f'<span class="stat-pill">{streak.get("total_stars", 0)} stars</span>',
                        f'<span class="stat-pill">{accuracy}% accuracy</span>',
                        '</div>',
                        '</div>',
                    ]
                )

                st.markdown(
                    profile_markup,
                    unsafe_allow_html=True,
                )

                col_a, col_b = st.columns([2, 1])
                with col_a:
                    if st.button("Select", key=f"select_child_{child['id']}", use_container_width=True):
                        st.session_state.active_child_id = child["id"]
                        st.session_state.page = "dashboard"
                        st.rerun()
                with col_b:
                    if st.button("Delete", key=f"delete_child_{child['id']}", use_container_width=True):
                        delete_child(child["id"])
                        st.rerun()

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button("Add new learner", use_container_width=True):
            st.session_state.page = "add_child"
            st.rerun()
