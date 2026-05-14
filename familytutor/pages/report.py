import html

import streamlit as st

from core.database import get_child, get_streak
from core.reports import get_report_data


def render():
    child_id = st.session_state.get("active_child_id")
    if not child_id:
        st.session_state.page = "home"
        st.rerun()

    child = get_child(child_id)
    streak = get_streak(child_id)

    st.markdown(
        f"""
        <div class="page-header">
            <h1>Progress Report</h1>
            <p class="subtitle">{html.escape(child['name'])} | Grade {child['grade']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading report..."):
        data = get_report_data(child_id)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _stat_card(f"{data['overall_accuracy']}%", "Overall accuracy", accent=True)
    with c2:
        _stat_card(data["total_questions"], "Total questions")
    with c3:
        _stat_card(streak.get("current_streak", 0), "Day streak")
    with c4:
        _stat_card(streak.get("total_stars", 0), "Stars earned")

    col_s, col_w = st.columns(2)
    with col_s:
        if data["strong_topics"]:
            st.markdown('<div class="insight-box strong"><div class="insight-title">Strong topics</div>', unsafe_allow_html=True)
            for topic in data["strong_topics"]:
                st.markdown(f"- {topic}")
            st.markdown("</div>", unsafe_allow_html=True)
    with col_w:
        if data["weak_topics"]:
            st.markdown('<div class="insight-box weak"><div class="insight-title">Needs more practice</div>', unsafe_allow_html=True)
            for topic in data["weak_topics"]:
                st.markdown(f"- {topic}")
            st.markdown("</div>", unsafe_allow_html=True)

    if data["chart_subjects"]:
        st.markdown("<h3>Accuracy by subject</h3>", unsafe_allow_html=True)
        st.image(f"data:image/png;base64,{data['chart_subjects']}", use_container_width=True)

    if data["chart_activity"]:
        st.markdown("<h3>Daily activity, last 14 days</h3>", unsafe_allow_html=True)
        st.image(f"data:image/png;base64,{data['chart_activity']}", use_container_width=True)

    if data["chart_topics"]:
        st.markdown("<h3>Topic accuracy breakdown</h3>", unsafe_allow_html=True)
        st.image(f"data:image/png;base64,{data['chart_topics']}", use_container_width=True)

    if data["recent"]:
        st.markdown("<h3>Recent sessions</h3>", unsafe_allow_html=True)
        for session in data["recent"]:
            accuracy = round(session["correct"] / session["total_questions"] * 100) if session["total_questions"] else 0
            st.markdown(
                f"""
                <div class="session-row">
                    <span class="session-subj">{html.escape(session['subject'])}</span>
                    <span class="session-topic">{html.escape(session['topic'])}</span>
                    <span class="session-score">{session['correct']}/{session['total_questions']} ({accuracy}%)</span>
                    <span class="session-date">{session['started_at'][:10]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if not data["total_questions"]:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">&#128202;</div>
                <div class="empty-text">No data yet</div>
                <div class="empty-sub">Complete a quiz to see progress here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("Back to dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


def _stat_card(value, label, accent=False):
    css_class = "stat-card accent" if accent else "stat-card"
    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="stat-val">{value}</div>
            <div class="stat-lbl">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
