import streamlit as st
from src.ask_language import AskLanguage
from src.ask_user_details import AskUserDetails
from src.ask_boyfriend_name import AskBoyfriendName  # 👈 new import
from src.welcome import Welcome

def main():
    st.set_page_config(page_title="Runaway Guys Demo", layout="centered")
    st.title("Demo App")

    if "user_details" not in st.session_state:
        st.session_state.user_details = {}

    # Step 1: Language
    if not st.session_state.user_details.get("language"):
        AskLanguage().run()

    # Step 2: User Details
    elif not st.session_state.user_details.get("name"):
        AskUserDetails().run()

    # Step 3: Boyfriend Name
    elif not st.session_state.user_details.get("bf_name"):
        AskBoyfriendName().run()

    # Step 4: Welcome
    elif not st.session_state.get("welcome_shown"):
        Welcome().run()

    # Debug panel
    st.subheader("🔎 Debug Info")
    st.json(st.session_state.user_details)


if __name__ == "__main__":
    main()
