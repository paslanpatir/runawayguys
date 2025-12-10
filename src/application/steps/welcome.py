"""Welcome step."""
import streamlit as st
from src.application.base_step import BaseStep


class Welcome(BaseStep):
    name = "welcome"

    def run(self):
        name = self.session.user_details.get("name", "User")

        st.markdown(self.msg.get("welcome_message", name=name))
        st.markdown(self.msg.get("welcome_description"))
        st.markdown(self.msg.get("welcome_instruction"))

        if not self.session.state.get("welcome_shown"):
            if st.button(self.msg.get("continue_msg")):
                self.session.state["welcome_shown"] = True
                st.rerun()

        return self.session.state.get("welcome_shown") is not None

