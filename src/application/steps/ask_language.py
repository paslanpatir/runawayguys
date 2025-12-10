"""Language selection step."""
import streamlit as st
from src.application.base_step import BaseStep


class AskLanguage(BaseStep):
    name = "language_selection"

    def run(self):
        if not self.session.user_details.get("language"):
            # Neutral prompt (before language is chosen)
            st.write(self.msg.get_any("language_prompt"))

            language = st.radio("Language / Dil", ["TR", "EN"], key="language_select")
            if st.button(self.msg.get_any("continue_msg")):
                self.session.user_details["language"] = language
                st.rerun()

        return self.session.user_details.get("language") is not None

