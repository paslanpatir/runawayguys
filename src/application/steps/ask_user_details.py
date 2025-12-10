"""User details collection step."""
import streamlit as st
from src.application.base_step import BaseStep
from src.utils.utils import is_valid_email


class AskUserDetails(BaseStep):
    name = "user_details"

    def run(self):
        msg = self.msg  # already initialized with language in BaseStep

        st.write(msg.get("enter_details_msg"))

        with st.form("user_details_form"):
            name = st.text_input(msg.get("name_input"), key="name_input")
            # Email is optional - if provided, results will be sent via email
            email = st.text_input(
                msg.get("email_input") + " (Optional)",
                key="email_input"
            )

            if st.form_submit_button(msg.get("continue_msg")):
                if name:
                    # If email is provided, validate it
                    if email:
                        if is_valid_email(email):
                            self.session.user_details["name"] = name
                            self.session.user_details["email"] = email
                            st.rerun()
                        else:
                            st.error(msg.get("enter_valid_email_msg"))
                    else:
                        # No email provided, just save name
                        self.session.user_details["name"] = name
                        self.session.user_details["email"] = None
                        st.rerun()
                else:
                    st.error(msg.get("enter_name_msg"))

        return self.session.user_details.get("name") is not None

