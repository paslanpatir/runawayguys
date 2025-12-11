"""User details collection step."""
import streamlit as st
from src.application.base_step import BaseStep
from src.utils.utils import is_valid_email


class AskUserDetails(BaseStep):
    name = "user_details"

    def run(self):
        msg = self.msg  # already initialized with language in BaseStep

        st.write(msg.get("enter_details_msg"))

        # Use a session state flag to track if form was submitted with errors
        form_error = st.session_state.get("user_details_form_error", None)
        if form_error:
            st.error(form_error)
            st.session_state.user_details_form_error = None  # Clear after showing

        with st.form("user_details_form"):
            name = st.text_input(msg.get("name_input"), key="name_input")
            # Email is optional - if provided, results will be sent via email
            email = st.text_input(
                msg.get("email_input") + " (Optional)",
                key="email_input"
            )
            # Show info message about email report
            st.caption(msg.get("email_report_info_msg"))

            if st.form_submit_button(msg.get("continue_msg")):
                if name:
                    # If email is provided, validate it
                    if email:
                        if is_valid_email(email):
                            self.session.user_details["name"] = name
                            self.session.user_details["email"] = email
                            # Clear any previous error
                            if "user_details_form_error" in st.session_state:
                                del st.session_state.user_details_form_error
                            st.rerun()
                        else:
                            st.session_state.user_details_form_error = msg.get("enter_valid_email_msg")
                            st.rerun()
                    else:
                        # No email provided, just save name
                        self.session.user_details["name"] = name
                        self.session.user_details["email"] = None
                        # Clear any previous error
                        if "user_details_form_error" in st.session_state:
                            del st.session_state.user_details_form_error
                        st.rerun()
                else:
                    st.session_state.user_details_form_error = msg.get("enter_name_msg")
                    st.rerun()

        return self.session.user_details.get("name") is not None

