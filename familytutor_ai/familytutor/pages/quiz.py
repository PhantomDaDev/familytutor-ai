import html

import streamlit as st

from core.ai_engine import generate_encouragement, generate_hint, generate_questions
from core.database import (
    create_session,
    end_session,
    get_child,
    save_answer,
    update_streak,
    update_topic_leitner,
)


def render():
    child_id = st.session_state.get("active_child_id")
    subject = st.session_state.get("selected_subject")
    topic = st.session_state.get("quiz_topic")
    topic_id = st.session_state.get("quiz_topic_id")
    difficulty = st.session_state.get("quiz_difficulty", 2)
    num_q = st.session_state.get("quiz_num_questions", 5)

    if not child_id or not subject or not topic:
        st.session_state.page = "dashboard"
        st.rerun()

    child = get_child(child_id)

    if not st.session_state.get("quiz_questions"):
        with st.spinner(f"Generating your {topic} quiz..."):
            st.session_state.quiz_questions = generate_questions(subject, topic, child["grade"], num_q, difficulty)
            st.session_state.quiz_session_id = create_session(child_id, subject, topic)
            st.session_state.quiz_results_saved = False

    questions = st.session_state.quiz_questions
    current = st.session_state.get("quiz_current", 0)
    answers = st.session_state.get("quiz_answers", [])
    session_id = st.session_state.get("quiz_session_id")

    if current >= len(questions):
        _render_results(child, questions, answers, session_id, topic_id, topic)
        return

    question = questions[current]
    st.markdown(
        f"""
        <div class="quiz-progress-wrap">
            <span class="quiz-progress-label">Question {current + 1} of {len(questions)}</span>
            <span class="quiz-subject-tag">{html.escape(subject)} | {html.escape(topic)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(current / len(questions))

    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-number">Q{current + 1}</div>
            <div class="question-text">{html.escape(question['question'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    answered_key = f"answered_{session_id}_{current}"
    selected_key = f"selected_{session_id}_{current}"
    hint_key = f"hint_{session_id}_{current}"
    answered = st.session_state.get(answered_key, False)
    selected = st.session_state.get(selected_key)

    if not answered and st.button("Get a hint"):
        with st.spinner("Thinking of a hint..."):
            st.session_state[hint_key] = generate_hint(question["question"], topic, child["grade"])

    if hint_key in st.session_state:
        st.info(st.session_state[hint_key])

    for index, option in enumerate(question["options"]):
        if answered:
            _render_answer_option(option, question["answer"], selected)
        else:
            if st.button(option, key=f"option_{current}_{index}", use_container_width=True):
                is_correct = option == question["answer"]
                st.session_state[selected_key] = option
                st.session_state[answered_key] = True
                answer = {
                    "question": question["question"],
                    "correct_answer": question["answer"],
                    "user_answer": option,
                    "is_correct": is_correct,
                    "explanation": question.get("explanation", ""),
                }
                st.session_state.quiz_answers = st.session_state.get("quiz_answers", []) + [answer]
                save_answer(session_id, question["question"], question["answer"], option, is_correct, question.get("explanation", ""))
                st.rerun()

    if answered:
        is_correct = selected == question["answer"]
        explanation = html.escape(question.get("explanation", ""))
        if is_correct:
            st.markdown(f'<div class="feedback correct">Correct. {explanation}</div>', unsafe_allow_html=True)
        else:
            answer = html.escape(question["answer"])
            st.markdown(f'<div class="feedback wrong">Not quite. The answer is <strong>{answer}</strong>. {explanation}</div>', unsafe_allow_html=True)

        label = "Finish quiz" if current + 1 >= len(questions) else "Next question"
        if st.button(label, key=f"next_{current}", use_container_width=True):
            st.session_state.quiz_current = current + 1
            st.rerun()


def _render_answer_option(option, correct_answer, selected):
    if option == correct_answer:
        css_class = "correct-answer"
        prefix = "Correct: "
    elif option == selected:
        css_class = "wrong-answer"
        prefix = "Selected: "
    else:
        css_class = "neutral-answer"
        prefix = ""

    st.markdown(
        f'<div class="answer-btn {css_class}">{prefix}{html.escape(option)}</div>',
        unsafe_allow_html=True,
    )


def _render_results(child, questions, answers, session_id, topic_id, topic):
    correct = sum(1 for answer in answers if answer["is_correct"])
    total = len(answers)
    score_pct = round(correct / total * 100) if total else 0
    overall_correct = score_pct >= 70
    stars = max(1, round(score_pct / 20))

    if not st.session_state.get("quiz_results_saved"):
        end_session(session_id, total, correct)
        if topic_id:
            update_topic_leitner(topic_id, overall_correct)
        update_streak(child["id"], stars)
        st.session_state.quiz_results_saved = True

    if score_pct >= 90:
        grade_label = "Excellent!"
        result_icon = "&#127942;"
    elif score_pct >= 70:
        grade_label = "Great job!"
        result_icon = "&#11088;"
    elif score_pct >= 50:
        grade_label = "Good effort!"
        result_icon = "&#128077;"
    else:
        grade_label = "Keep practising!"
        result_icon = "&#128170;"

    with st.spinner("Preparing your results..."):
        message = generate_encouragement(overall_correct, child["name"], correct, total)

    st.markdown(
        f"""
        <div class="results-header">
            <div class="results-emoji">{result_icon}</div>
            <div class="results-title">{grade_label}</div>
            <div class="results-score">{correct}/{total} correct</div>
            <div class="results-pct">{score_pct}%</div>
            <div class="results-message">{html.escape(message)}</div>
            <div class="stars-earned">{stars} stars earned</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if overall_correct:
        st.success(f"Great work. {topic} moved to the next Leitner box.")
    else:
        st.warning(f"{topic} needs more practice, so it will come up again sooner.")

    st.markdown("<h3>Review your answers</h3>", unsafe_allow_html=True)
    for index, answer in enumerate(answers):
        status = "Correct" if answer["is_correct"] else "Review"
        with st.expander(f"{status} - Q{index + 1}: {answer['question'][:80]}"):
            st.markdown(f"**Your answer:** {answer['user_answer']}")
            st.markdown(f"**Correct answer:** {answer['correct_answer']}")
            if answer.get("explanation"):
                st.info(answer["explanation"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try again", use_container_width=True):
            _reset_quiz_state()
            st.session_state.page = "quiz"
            st.rerun()
    with col2:
        if st.button("Back to dashboard", use_container_width=True):
            _reset_quiz_state()
            st.session_state.page = "dashboard"
            st.rerun()


def _reset_quiz_state():
    st.session_state.quiz_questions = None
    st.session_state.quiz_current = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_session_id = None
    st.session_state.quiz_results_saved = False
