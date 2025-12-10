"""Goodbye step - wrapper for Goodbye with DB write capability."""
import streamlit as st
from src.base_step import BaseStep
from src.database_handler import DatabaseHandler
from src.utils import safe_decimal
from datetime import datetime


class GoodbyeStep(BaseStep):
    name = "goodbye"

    def __init__(self, db_write_allowed=False):
        super().__init__()
        self.db_write_allowed = db_write_allowed

    def run(self):
        name = self.session.user_details.get("name", "User")
        msg = self.msg

        st.markdown(msg.get("goodbye_message", name=name))
        st.balloons()

        # Save data if write is allowed
        if self.db_write_allowed:
            self._save_all_data()

        return True

    def _save_all_data(self):
        """Save all session data to database."""
        db_handler = DatabaseHandler(db_write_allowed=self.db_write_allowed)

        try:
            # Save session responses
            if self.session.state.get("redflag_responses") and self.session.state.get("filter_responses"):
                self._save_session_response(db_handler)

            # Save GTK responses
            if self.session.state.get("extra_questions_responses"):
                self._save_gtk_response(db_handler)

            # Save toxicity rating
            if self.session.state.get("toxicity_rating"):
                self._save_toxicity_rating(db_handler)

            # Save feedback
            if self.session.state.get("feedback_rating"):
                self._save_feedback(db_handler)

            db_handler.close()
        except Exception as e:
            msg = self.msg
            st.error(msg.get("response_error_msg", e=str(e)))

    def _save_session_response(self, db_handler):
        """Save main session response data."""
        user_id = self.session.user_details["user_id"]
        session_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        newdata_dict = {
            "user_id": user_id,
            "name": self.session.user_details["name"],
            "email": self.session.user_details["email"],
            "boyfriend_name": self.session.user_details["bf_name"],
            "language": self.session.user_details["language"],
            "toxic_score": safe_decimal(self.session.state.get("toxic_score")),
            "filter_violations": safe_decimal(self.session.state.get("filter_violations", 0)),
            "session_start_time": self.session.state.get("session_start_time"),
            "session_end_time": session_end_time,
            **{k: safe_decimal(v) for k, v in self.session.state.get("redflag_responses", {}).items()},
            **{k: safe_decimal(v) for k, v in self.session.state.get("filter_responses", {}).items()},
        }

        db_handler.add_record("session_responses", newdata_dict)

    def _save_gtk_response(self, db_handler):
        """Save GetToKnow questions responses."""
        newdata_dict = {
            "user_id": self.session.user_details["user_id"],
            "name": self.session.user_details["name"],
            "email": self.session.user_details["email"],
            "boyfriend_name": self.session.user_details["bf_name"],
            "language": self.session.user_details["language"],
            "test_date": self.session.state.get("session_start_time"),
            **self.session.state.get("extra_questions_responses", {}),
        }

        db_handler.add_record("session_gtk_responses", newdata_dict)

    def _save_toxicity_rating(self, db_handler):
        """Save toxicity rating."""
        newdata_dict = {
            "user_id": self.session.user_details["user_id"],
            "name": self.session.user_details["name"],
            "email": self.session.user_details["email"],
            "boyfriend_name": self.session.user_details["bf_name"],
            "language": self.session.user_details["language"],
            "test_date": self.session.state.get("session_start_time"),
            "toxicity_rating": self.session.state.get("toxicity_rating"),
        }

        db_handler.add_record("session_toxicity_rating", newdata_dict)

    def _save_feedback(self, db_handler):
        """Save feedback rating."""
        newdata_dict = {
            "user_id": self.session.user_details["user_id"],
            "user_name": self.session.user_details["name"],
            "email": self.session.user_details["email"],
            "boyfriend_name": self.session.user_details["bf_name"],
            "language": self.session.user_details["language"],
            "test_date": self.session.state.get("session_start_time"),
            "rating": self.session.state.get("feedback_rating"),
        }

        db_handler.add_record("session_feedback", newdata_dict)

