import html

import streamlit as st


def render():
    child_id = st.session_state.get("active_child_id")
    topic = st.session_state.get("quiz_topic")
    subject = st.session_state.get("selected_subject")
    if not child_id or not topic or not subject:
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown(
        f"""
        <div class="page-header">
            <h1>Configure your quiz</h1>
            <p class="subtitle">{html.escape(subject)} | {html.escape(topic)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
    with col2:
        num_questions = st.slider("Number of questions", min_value=3, max_value=10, value=5)

    st.markdown(
        f"""
        <div class="config-preview">
            <div class="config-item"><span>Topic</span><strong>{html.escape(topic)}</strong></div>
            <div class="config-item"><span>Difficulty</span><strong>{difficulty}</strong></div>
            <div class="config-item"><span>Questions</span><strong>{num_questions}</strong></div>
            <div class="config-item"><span>Question source</span><strong>AI with local fallback</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Back", use_container_width=True):
            st.session_state.page = "quiz_setup"
            st.rerun()
    with col_b:
        if st.button("Start quiz", use_container_width=True):
            st.session_state.quiz_difficulty = {"Easy": 1, "Medium": 2, "Hard": 3}[difficulty]
            st.session_state.quiz_num_questions = num_questions
            st.session_state.quiz_questions = None
            st.session_state.quiz_current = 0
            st.session_state.quiz_answers = []
            st.session_state.quiz_session_id = None
            st.session_state.quiz_results_saved = False
            st.session_state.page = "quiz"
            st.rerun()
