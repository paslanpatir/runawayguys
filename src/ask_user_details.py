import streamlit as st
from src.base_step import BaseStep
from src.utils import is_valid_email


class AskUserDetails(BaseStep):
    name = "user_details"

    def run(self):
        msg = self.msg  # already initialized with language in BaseStep

        st.write(msg.get("enter_details_msg"))

        with st.form("user_details_form"):
            name = st.text_input(msg.get("name_input"), key="name_input")
            email = st.text_input(msg.get("email_input"), key="email_input")

            if st.form_submit_button(msg.get("continue_msg")):
                if name:
                    if email and is_valid_email(email):
                        self.session.user_details["name"] = name
                        self.session.user_details["email"] = email
                        st.rerun()
                    else:
                        st.error(msg.get("enter_valid_email_msg"))
                else:
                    st.error(msg.get("enter_name_msg"))

        return (
            self.session.user_details.get("name") is not None
            and self.session.user_details.get("email") is not None
        )
