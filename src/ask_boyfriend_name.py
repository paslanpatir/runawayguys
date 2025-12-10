import streamlit as st
from src.base_step import BaseStep


class AskBoyfriendName(BaseStep):
    name = "boyfriend_name"

    def run(self):
        msg = self.msg

        st.write(msg.get("enter_bf_name_msg"))

        with st.form("bf_name_form"):
            bf_name = st.text_input(msg.get("bf_name_input"), key="bf_name_input")
            if st.form_submit_button(msg.get("continue_msg")):
                if bf_name:
                    self.session.user_details["bf_name"] = bf_name
                    st.rerun()
                else:
                    st.error(msg.get("enter_bf_name_msg"))
        return self.session.user_details.get("bf_name") is not None
                