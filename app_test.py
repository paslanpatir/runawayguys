import streamlit as st
from src.ask_language import AskLanguage
from src.ask_user_details import AskUserDetails
from src.ask_boyfriend_name import AskBoyfriendName
from src.welcome import Welcome
from src.ask_filter_questions import AskFilterQuestions

from src.progress_manager import ProgressManager


def main():
    st.set_page_config(page_title="Runaway Guys Demo", layout="centered")
    st.title("Demo App")

    if "user_details" not in st.session_state:
        st.session_state.user_details = {}

    if "welcome_shown" not in st.session_state:
        st.session_state.welcome_shown = False

    # ✅ Define steps in order
    steps = [AskLanguage, AskUserDetails, AskBoyfriendName, Welcome]
    pm = ProgressManager(steps)

    current_step = None

    # Step 1: Language
    if not st.session_state.user_details.get("language"):
        current_step = AskLanguage.name
        #AskLanguage().run()
        st.session.user_details["language"] = 'EN'

    # Step 2: User Details
    elif not st.session_state.user_details.get("name"):
        current_step = AskUserDetails.name
        #AskUserDetails().run()
        st.session.user_details["name"] = 'Test User'
        st.session.user_details["email"] = 'test@user.com'

    # Step 3: Boyfriend Name
    elif not st.session_state.user_details.get("bf_name"):
        current_step = AskBoyfriendName.name
        #AskBoyfriendName().run()
        st.session_state.user_details["bf_name"] = 'Test BF'

    # Step 4: Welcome
    elif not st.session_state.get("welcome_shown"):
        current_step = Welcome.name
        #Welcome().run()
        st.session.state["welcome_shown"] = True

    # Step 5: Filter Questions
    elif not st.session_state.get("filter_responses"):
        current_step = AskFilterQuestions.name
        AskFilterQuestions().run()
        #st.session.state["welcome_shown"] = True

    # ✅ Show progress bar
    if current_step:
        pm.show_progress(current_step)

    # Debug panel
    st.subheader("🔎 Debug Info")
    debug_info = {
    "user_details": st.session_state.user_details,
    "welcome_shown": st.session_state.get("welcome_shown", False),
    "survey_completed": st.session_state.get("survey_completed", False),
    "counter": st.session_state.get("counter", 0),
    "filter_responses": st.session_state.get("filter_responses", None),
    "filter_violations": st.session_state.get("filter_violations", None),
    }
    st.json(debug_info)


if __name__ == "__main__":
    main()
