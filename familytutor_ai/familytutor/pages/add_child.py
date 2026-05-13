import streamlit as st

from core.database import AVAILABLE_SUBJECTS, AVATARS, create_child


AVATAR_LABELS = {
    "star": "Star",
    "rocket": "Rocket",
    "dragon": "Dragon",
    "unicorn": "Unicorn",
    "robot": "Robot",
    "owl": "Owl",
    "lion": "Lion",
    "fox": "Fox",
}


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>Add a new learner</h1>
            <p class="subtitle">Set up a personalized tutoring profile.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("add_child_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Child's name", placeholder="e.g. Alex")
        with col2:
            grade = st.selectbox("Grade", list(range(1, 13)), index=4)

        avatar = st.radio(
            "Avatar",
            AVATARS,
            format_func=lambda item: AVATAR_LABELS.get(item, item.title()),
            horizontal=True,
        )

        subjects = st.multiselect(
            "Subjects",
            AVAILABLE_SUBJECTS,
            default=["Mathematics", "Science", "English"],
        )

        submitted = st.form_submit_button("Create profile", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Please enter a name.")
        elif not subjects:
            st.error("Please select at least one subject.")
        else:
            child_id = create_child(name.strip(), grade, avatar, subjects)
            st.session_state.active_child_id = child_id
            st.session_state.page = "dashboard"
            st.success(f"Welcome, {name.strip()}!")
            st.rerun()

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()
