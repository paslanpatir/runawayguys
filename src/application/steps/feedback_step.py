"""Feedback step."""
import streamlit as st
from src.application.base_step import BaseStep
from src.adapters.database.database_handler import DatabaseHandler
from src.domain.value_objects import FeedbackRecord, UserDetails
from src.utils.session_id_generator import generate_session_id
import pandas as pd


class FeedbackStep(BaseStep):
    name = "feedback"
    
    def __init__(self, db_write_allowed=False):
        super().__init__()
        self.db_write_allowed = db_write_allowed

    def run(self):
        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("enter_feedback_msg"), divider=True)

        sentiment_mapping = msg.get("sentiment_mapping")
        selected = st.feedback("stars")

        if selected is None:
            st.warning(msg.get("please_rate_msg"))
            rating = None
        else:
            # Convert feedback to 1-based index
            rating = selected + 1
            st.markdown(msg.get("feedback_result_msg", star=sentiment_mapping[rating - 1]))

        if st.button(msg.get("continue_msg")):
            if rating:
                self.session.state["feedback_rating"] = rating
                # Save feedback to database (only once)
                if not self.session.state.get("feedback_saved", False):
                    self._save_feedback()
                    self.session.state["feedback_saved"] = True
                    # Show toast message when feedback is saved
                    feedback_msg = msg.get("response_saved_msg") if msg.texts.get("response_saved_msg") else "Feedback saved successfully!"
                    st.toast(feedback_msg, icon="✅")
                st.rerun()
            else:
                st.error(msg.get("please_rate_msg"))

        return self.session.state.get("feedback_rating") is not None
    
    def _save_feedback(self):
        """Save feedback rating using FeedbackRecord value object."""
        db_handler = DatabaseHandler(db_write_allowed=self.db_write_allowed)
        
        try:
            user_details = UserDetails(
                user_id=self.session.user_details["user_id"],
                name=self.session.user_details["name"],
                email=self.session.user_details["email"],
                language=self.session.user_details["language"],
                bf_name=self.session.user_details["bf_name"],
            )

            session_id = generate_session_id(user_details.user_id, user_details.bf_name)

            # Create FeedbackRecord value object
            feedback = FeedbackRecord(
                id=session_id,
                user_id=user_details.user_id,
                user_name=user_details.name,
                email=user_details.email,
                boyfriend_name=user_details.bf_name,
                language=user_details.language,
                test_date=self.session.state.get("session_start_time"),
                rating=self.session.state.get("feedback_rating"),
            )

            # Convert to dict and save (or update if record already exists)
            record_dict = feedback.to_dict()
            try:
                existing = db_handler.load_table("session_feedback")
                if not existing.empty:
                    existing["id"] = pd.to_numeric(existing["id"], errors='coerce')
                    if session_id in existing["id"].values:
                        db_handler.update_record("session_feedback", {"id": session_id}, record_dict)
                        print(f"[OK] Updated existing feedback record (id: {session_id})")
                    else:
                        db_handler.add_record("session_feedback", record_dict)
                        print(f"[OK] Created new feedback record (id: {session_id})")
                else:
                    db_handler.add_record("session_feedback", record_dict)
                    print(f"[OK] Created new feedback record (id: {session_id})")
            except Exception:
                db_handler.add_record("session_feedback", record_dict)
            
            db_handler.close()
        except Exception as e:
            print(f"[ERROR] Failed to save feedback: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")

