import streamlit as st
from src.ask_language import AskLanguage
from src.ask_user_details import AskUserDetails
from src.ask_boyfriend_name import AskBoyfriendName
from src.welcome import Welcome
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
        AskLanguage().run()

    # Step 2: User Details
    elif not st.session_state.user_details.get("name"):
        current_step = AskUserDetails.name
        AskUserDetails().run()

    # Step 3: Boyfriend Name
    elif not st.session_state.user_details.get("bf_name"):
        current_step = AskBoyfriendName.name
        AskBoyfriendName().run()

    # Step 4: Welcome
    elif not st.session_state.get("welcome_shown"):
        current_step = Welcome.name
        Welcome().run()

    # ✅ Show progress bar
    if current_step:
        pm.show_progress(current_step)

    # Debug panel
    st.subheader("🔎 Debug Info")
    st.json(st.session_state.user_details)


if __name__ == "__main__":
    main()
