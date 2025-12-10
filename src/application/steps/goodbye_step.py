"""Goodbye step - wrapper for Goodbye with DB write capability."""
import streamlit as st
from src.application.base_step import BaseStep
from src.adapters.database.database_handler import DatabaseHandler
from src.domain.value_objects import (
    SessionResponse,
    GTKResponseRecord,
    ToxicityRatingRecord,
    FeedbackRecord,
    UserDetails,
)
from src.utils.utils import safe_decimal
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

        # Save data only once (check if already saved)
        if not self.session.state.get("data_saved", False):
            # Always save data - backend is chosen based on db_write_allowed flag
            # If False, saves to CSV; if True, saves to DynamoDB
            self._save_all_data()
            self.session.state["data_saved"] = True

        # Show option to start a new survey
        st.divider()
        button_text = msg.get("start_new_survey")
        if st.button(button_text):
            # Reset survey states but keep user_id and name
            self.session.reset_for_new_survey()
            st.rerun()

        # Don't return True immediately - stay on this page until user clicks "Start New Survey"
        return False

    def _save_all_data(self):
        """Save all session data to database (CSV or DynamoDB based on flag)."""
        # Always create handler - it will use CSV if db_write_allowed=False, DynamoDB if True
        db_handler = DatabaseHandler(db_write_allowed=self.db_write_allowed)

        try:
            # Save session responses
            if self.session.state.get("redflag_responses") and self.session.state.get("filter_responses"):
                self._save_session_response(db_handler)
                st.success(self.msg.get("response_saved_msg"))

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
        """Save main session response data using SessionResponse value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        session_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get next ID by checking existing records
        try:
            existing = db_handler.load_table("session_responses")
            next_id = len(existing) + 1 if not existing.empty else 1
        except (FileNotFoundError, Exception):
            next_id = 1

        # Create SessionResponse value object
        session_response = SessionResponse(
            id=next_id,
            user_id=user_details.user_id,
            name=user_details.name,
            email=user_details.email,
            boyfriend_name=user_details.bf_name,
            language=user_details.language,
            toxic_score=safe_decimal(self.session.state.get("toxic_score")),
            filter_violations=safe_decimal(self.session.state.get("filter_violations", 0)),
            session_start_time=self.session.state.get("session_start_time"),
            result_start_time=self.session.state.get("result_start_time"),
            session_end_time=session_end_time,
            redflag_responses={k: safe_decimal(v) for k, v in self.session.state.get("redflag_responses", {}).items()},
            filter_responses={k: safe_decimal(v) for k, v in self.session.state.get("filter_responses", {}).items()},
        )

        # Convert to dict and save
        db_handler.add_record("session_responses", session_response.to_dict())

    def _save_gtk_response(self, db_handler):
        """Save GetToKnow questions responses using GTKResponseRecord value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        # Get next ID by checking existing records
        try:
            existing = db_handler.load_table("session_gtk_responses")
            next_id = len(existing) + 1 if not existing.empty else 1
        except (FileNotFoundError, Exception):
            next_id = 1

        # Create GTKResponseRecord value object
        gtk_response = GTKResponseRecord(
            id=next_id,
            user_id=user_details.user_id,
            name=user_details.name,
            email=user_details.email,
            boyfriend_name=user_details.bf_name,
            language=user_details.language,
            test_date=self.session.state.get("session_start_time"),
            gtk_responses=self.session.state.get("extra_questions_responses", {}),
        )

        # Convert to dict and save
        db_handler.add_record("session_gtk_responses", gtk_response.to_dict())

    def _save_toxicity_rating(self, db_handler):
        """Save toxicity rating using ToxicityRatingRecord value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        # Get next ID by checking existing records
        try:
            existing = db_handler.load_table("session_toxicity_rating")
            next_id = len(existing) + 1 if not existing.empty else 1
        except (FileNotFoundError, Exception):
            next_id = 1

        # Create ToxicityRatingRecord value object
        toxicity_rating = ToxicityRatingRecord(
            id=next_id,
            user_id=user_details.user_id,
            name=user_details.name,
            email=user_details.email,
            boyfriend_name=user_details.bf_name,
            language=user_details.language,
            test_date=self.session.state.get("session_start_time"),
            toxicity_rating=self.session.state.get("toxicity_rating"),
        )

        # Convert to dict and save
        db_handler.add_record("session_toxicity_rating", toxicity_rating.to_dict())

    def _save_feedback(self, db_handler):
        """Save feedback rating using FeedbackRecord value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        # Get next ID by checking existing records
        try:
            existing = db_handler.load_table("session_feedback")
            next_id = len(existing) + 1 if not existing.empty else 1
        except (FileNotFoundError, Exception):
            next_id = 1

        # Create FeedbackRecord value object
        feedback = FeedbackRecord(
            id=next_id,
            user_id=user_details.user_id,
            user_name=user_details.name,
            email=user_details.email,
            boyfriend_name=user_details.bf_name,
            language=user_details.language,
            test_date=self.session.state.get("session_start_time"),
            rating=self.session.state.get("feedback_rating"),
        )

        # Convert to dict and save
        db_handler.add_record("session_feedback", feedback.to_dict())
