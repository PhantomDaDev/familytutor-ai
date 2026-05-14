import html

import streamlit as st

from core.database import get_all_topics, get_child, get_due_topics


def render():
    child_id = st.session_state.get("active_child_id")
    subject = st.session_state.get("selected_subject")
    if not child_id or not subject:
        st.session_state.page = "dashboard"
        st.rerun()

    child = get_child(child_id)
    due_topics = get_due_topics(child_id, subject)
    all_topics = get_all_topics(child_id, subject)

    st.markdown(
        f"""
        <div class="page-header">
            <h1>{html.escape(subject)} Quiz</h1>
            <p class="subtitle">Choose what to practise, {html.escape(child['name'])}.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if due_topics:
        st.markdown('<div class="section-label">Due for review</div>', unsafe_allow_html=True)
        for topic in due_topics:
            _topic_row(topic, "Review", "due")

    st.markdown('<div class="section-label" style="margin-top:1.5rem">All topics</div>', unsafe_allow_html=True)
    for topic in all_topics:
        _topic_row(topic, "Practise", "all")

    st.markdown("---")
    if st.button("Back to dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


def _topic_row(topic, button_label, key_prefix):
    col1, col2 = st.columns([3, 1])
    with col1:
        row_class = "topic-row due" if key_prefix == "due" else "topic-row"
        st.markdown(
            f"""
            <div class="{row_class}">
                <span class="topic-name">{html.escape(topic['topic'])}</span>
                <span class="topic-meta">Leitner box {topic['box']}/5 | {topic.get('correct_streak', 0)} correct streak</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button(button_label, key=f"{key_prefix}_{topic['id']}", use_container_width=True):
            st.session_state.quiz_topic = topic["topic"]
            st.session_state.quiz_topic_id = topic["id"]
            st.session_state.page = "quiz_config"
            st.rerun()
