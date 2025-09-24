import streamlit as st
from src.base_step import BaseStep
from src.messages import Message

class AskBoyfriendName(BaseStep):
    name = "boyfriend_name"

    def run(self):
        language = st.session_state.user_details.get("language", "EN")
        msg = Message(language)

        st.write(msg.get_text("enter_bf_name_msg"))

        with st.form("bf_name_form"):
            bf_name = st.text_input(msg.get_text("bf_name_input"), key="bf_name_input")
            if st.form_submit_button(msg.get_text("continue_msg")):
                if bf_name:
                    st.session_state.user_details["bf_name"] = bf_name
                    st.rerun()
                else:
                    st.error(msg.get_text("enter_bf_name_msg"))
