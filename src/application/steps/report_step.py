"""Report step - sends automatic results via email if requested."""
import streamlit as st
from src.application.base_step import BaseStep
from src.adapters.email.email_adapter import send_survey_report


class ReportStep(BaseStep):
    name = "report"

    def run(self):
        """
        Send automatic report via email if user requested it.
        """
        msg = self.msg
        
        email = self.session.user_details.get("email")
        
        if email:
            # Prepare session data for email
            session_data = {
                "user_details": self.session.user_details,
                "toxic_score": self.session.state.get("toxic_score", 0),
                "filter_violations": self.session.state.get("filter_violations", 0),
            }
            
            # Send email
            language = self.session.user_details.get("language", "EN")
            success = send_survey_report(
                recipient_email=email,
                session_data=session_data,
                language=language,
            )
            
            if success:
                st.success(msg.get("report_sent_to_msg", email=email))
                self.session.state["report_sent"] = True
            else:
                st.warning("Email could not be sent. Please check your email configuration.")
                self.session.state["report_sent"] = False
        else:
            # No email requested, skip
            self.session.state["report_sent"] = False
            st.info(msg.get("report_skipped_msg"))
        
        return True

