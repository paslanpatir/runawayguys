"""Goodbye step - wrapper for Goodbye with DB write capability."""
import streamlit as st
from decimal import Decimal
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
from src.utils.constants import DATE_FORMAT


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

        # Show contact information
        st.markdown(msg.get("contact_email_info_msg"))

        # Show option to start a new survey
        button_text = msg.get("start_new_survey")
        if st.button(button_text):
            # Reset survey states but keep user_id and name
            self.session.reset_for_new_survey()
            st.rerun()

        # Don't return True immediately - stay on this page until user clicks "Start New Survey"
        return False

    def _save_feedback_only(self):
        """Save only feedback to database (CSV or DynamoDB based on flag)."""
        # Main data is saved in report_step, only save feedback here
        db_handler = DatabaseHandler(db_write_allowed=self.db_write_allowed)

        try:
            # Save feedback
            if self.session.state.get("feedback_rating"):
                self._save_feedback(db_handler)
                st.success(self.msg.get("feedback_saved_msg", default="Feedback saved successfully!"))

            db_handler.close()
        except Exception as e:
            msg = self.msg
            st.error(msg.get("response_error_msg", e=str(e)))
    
    # Keep these methods for backward compatibility (used by report_step)
    def _save_session_response(self, db_handler):
        """Kept for backward compatibility - now saved in report_step."""
        pass
    
    def _save_gtk_response(self, db_handler):
        """Kept for backward compatibility - now saved in report_step."""
        pass
    
    def _save_toxicity_rating(self, db_handler):
        """Kept for backward compatibility - now saved in report_step."""
        pass
    
    def _update_summary_statistics(self, db_handler):
        """Kept for backward compatibility - now saved in report_step."""
        pass
    
    def _save_session_insights(self, db_handler):
        """Kept for backward compatibility - now saved in report_step."""
        pass

    def _save_session_response(self, db_handler):
        """Save main session response data using SessionResponse value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        session_end_time = datetime.now().strftime(DATE_FORMAT)
        
        # Get or create session_id based on user_id and boyfriend_name
        from src.utils.session_id_generator import get_or_create_session_id
        session_id = get_or_create_session_id(
            db_handler=db_handler,
            table_name="session_responses",
            user_id=user_details.user_id,
            boyfriend_name=user_details.bf_name,
        )

        # Create SessionResponse value object
        session_response = SessionResponse(
            id=session_id,
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

        # Convert to dict and save (or update if record already exists)
        record_dict = session_response.to_dict()
        # Check if record with this ID already exists
        try:
            existing = db_handler.load_table("session_responses")
            if not existing.empty and session_id in existing["id"].values:
                # Record exists, update it
                db_handler.update_record("session_responses", {"id": session_id}, record_dict)
                print(f"[OK] Updated existing session_response record (id: {session_id})")
            else:
                # New record, add it
                db_handler.add_record("session_responses", record_dict)
                print(f"[OK] Created new session_response record (id: {session_id})")
        except Exception:
            # If we can't check, just add (will overwrite in DynamoDB if exists)
            db_handler.add_record("session_responses", record_dict)

    def _save_gtk_response(self, db_handler):
        """Save GetToKnow questions responses using GTKResponseRecord value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        # Get or create session_id based on user_id and boyfriend_name
        from src.utils.session_id_generator import get_or_create_session_id
        session_id = get_or_create_session_id(
            db_handler=db_handler,
            table_name="session_gtk_responses",
            user_id=user_details.user_id,
            boyfriend_name=user_details.bf_name,
        )

        # Create GTKResponseRecord value object
        gtk_response = GTKResponseRecord(
            id=session_id,
            user_id=user_details.user_id,
            name=user_details.name,
            email=user_details.email,
            boyfriend_name=user_details.bf_name,
            language=user_details.language,
            test_date=self.session.state.get("session_start_time"),
            gtk_responses=self.session.state.get("extra_questions_responses", {}),
        )

        # Convert to dict and save (or update if record already exists)
        record_dict = gtk_response.to_dict()
        try:
            existing = db_handler.load_table("session_gtk_responses")
            if not existing.empty and session_id in existing["id"].values:
                db_handler.update_record("session_gtk_responses", {"id": session_id}, record_dict)
                print(f"[OK] Updated existing gtk_response record (id: {session_id})")
            else:
                db_handler.add_record("session_gtk_responses", record_dict)
                print(f"[OK] Created new gtk_response record (id: {session_id})")
        except Exception:
            db_handler.add_record("session_gtk_responses", record_dict)

    def _save_toxicity_rating(self, db_handler):
        """Save toxicity rating using ToxicityRatingRecord value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        # Get or create session_id based on user_id and boyfriend_name
        from src.utils.session_id_generator import get_or_create_session_id
        session_id = get_or_create_session_id(
            db_handler=db_handler,
            table_name="session_toxicity_rating",
            user_id=user_details.user_id,
            boyfriend_name=user_details.bf_name,
        )

        # Create ToxicityRatingRecord value object
        toxicity_rating = ToxicityRatingRecord(
            id=session_id,
            user_id=user_details.user_id,
            name=user_details.name,
            email=user_details.email,
            boyfriend_name=user_details.bf_name,
            language=user_details.language,
            test_date=self.session.state.get("session_start_time"),
            toxicity_rating=self.session.state.get("toxicity_rating"),
        )

        # Convert to dict and save (or update if record already exists)
        record_dict = toxicity_rating.to_dict()
        try:
            existing = db_handler.load_table("session_toxicity_rating")
            if not existing.empty and session_id in existing["id"].values:
                db_handler.update_record("session_toxicity_rating", {"id": session_id}, record_dict)
                print(f"[OK] Updated existing toxicity_rating record (id: {session_id})")
            else:
                db_handler.add_record("session_toxicity_rating", record_dict)
                print(f"[OK] Created new toxicity_rating record (id: {session_id})")
        except Exception:
            db_handler.add_record("session_toxicity_rating", record_dict)

    def _save_feedback(self, db_handler):
        """Save feedback rating using FeedbackRecord value object."""
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )

        # Get or create session_id based on user_id and boyfriend_name
        from src.utils.session_id_generator import get_or_create_session_id
        session_id = get_or_create_session_id(
            db_handler=db_handler,
            table_name="session_feedback",
            user_id=user_details.user_id,
            boyfriend_name=user_details.bf_name,
        )

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
            if not existing.empty and session_id in existing["id"].values:
                db_handler.update_record("session_feedback", {"id": session_id}, record_dict)
                print(f"[OK] Updated existing feedback record (id: {session_id})")
            else:
                db_handler.add_record("session_feedback", record_dict)
                print(f"[OK] Created new feedback record (id: {session_id})")
        except Exception:
            db_handler.add_record("session_feedback", record_dict)
    
    def _update_summary_statistics(self, db_handler):
        """Update Summary_Sessions table with new session data."""
        try:
            # Get current values from session state (loaded at app start)
            cur_toxic_score = Decimal(str(self.session.state.get("toxic_score", 0)))
            cur_filter_violations = int(self.session.state.get("filter_violations", 0))
            
            # Get existing summary values (with defaults if not set)
            sum_toxic_score = Decimal(str(self.session.state.get("sum_toxic_score", 0)))
            max_toxic_score = Decimal(str(self.session.state.get("max_toxic_score", 0)))
            min_toxic_score = Decimal(str(self.session.state.get("min_toxic_score", 1)))
            count_guys = int(self.session.state.get("count_guys", 0))
            sum_filter_violations = int(self.session.state.get("sum_filter_violations", 0))
            
            # Update values
            sum_toxic_score = sum_toxic_score + cur_toxic_score
            count_guys = count_guys + 1
            avg_toxic_score = Decimal("1.0") * sum_toxic_score / Decimal(str(count_guys))
            
            # Update max and min toxic scores
            if max_toxic_score < cur_toxic_score:
                max_toxic_score = cur_toxic_score
            if min_toxic_score > cur_toxic_score:
                min_toxic_score = cur_toxic_score
            
            # Update filter violations
            sum_filter_violations = sum_filter_violations + cur_filter_violations
            avg_filter_violations = Decimal("1.0") * Decimal(str(sum_filter_violations)) / Decimal(str(count_guys))
            
            # Note: max_id tracking removed - IDs are now hash-based and order-agnostic
            # We no longer need to track max IDs since session_ids are generated deterministically
            # from user_id + boyfriend_name, not sequentially
            
            last_date = self.session.state.get("session_start_time", datetime.now().strftime(DATE_FORMAT))
            
            # Prepare update dictionary
            update_dict = {
                "sum_toxic_score": float(sum_toxic_score),
                "max_toxic_score": float(max_toxic_score),
                "min_toxic_score": float(min_toxic_score),
                "avg_toxic_score": float(avg_toxic_score),
                "sum_filter_violations": sum_filter_violations,
                "avg_filter_violations": float(avg_filter_violations),
                "count_guys": count_guys,
                # max_id fields kept for backward compatibility but set to 0 (no longer tracked)
                "max_id_session_responses": 0,
                "max_id_gtk_responses": 0,
                "max_id_feedback": 0,
                "max_id_session_toxicity_rating": 0,
                "last_update_date": last_date,
            }
            
            # Check if Summary_Sessions table exists and has a record
            try:
                summary = db_handler.load_table("Summary_Sessions")
                if summary.empty:
                    # Create initial record
                    update_dict["summary_id"] = 1
                    db_handler.add_record("Summary_Sessions", update_dict)
                    print("[OK] Created initial Summary_Sessions record")
                else:
                    # Update existing record (summary_id = 1)
                    db_handler.update_record("Summary_Sessions", {"summary_id": 1}, update_dict)
                    print(f"[OK] Updated Summary_Sessions. New avg_toxic_score: {float(avg_toxic_score):.4f}")
            except (FileNotFoundError, Exception) as e:
                # Table doesn't exist or error loading, create it
                update_dict["summary_id"] = 1
                db_handler.add_record("Summary_Sessions", update_dict)
                print(f"[OK] Created Summary_Sessions table with initial record (error: {e})")
            
            # Update session state with new values
            self.session.state["sum_toxic_score"] = sum_toxic_score
            self.session.state["max_toxic_score"] = max_toxic_score
            self.session.state["min_toxic_score"] = min_toxic_score
            self.session.state["avg_toxic_score"] = avg_toxic_score
            self.session.state["sum_filter_violations"] = sum_filter_violations
            self.session.state["avg_filter_violations"] = avg_filter_violations
            self.session.state["count_guys"] = count_guys
            # max_id fields no longer tracked in session state
            
        except Exception as e:
            print(f"[ERROR] Failed to update Summary_Sessions: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
    
    def _save_session_insights(self, db_handler):
        """Save session insights to database (CSV or DynamoDB)."""
        try:
            insight_metadata = self.session.state.get("insight_metadata")
            if not insight_metadata:
                return
            
            from typing import List, Tuple, Optional
            
            # Extract data from metadata
            user_id = insight_metadata.get("user_id", "unknown")
            user_name = insight_metadata.get("user_name", "User")
            email = insight_metadata.get("email")
            bf_name = insight_metadata.get("bf_name", "Your boyfriend")
            language = insight_metadata.get("language", "EN")
            toxic_score = insight_metadata.get("toxic_score", 0.0)
            avg_toxic_score = insight_metadata.get("avg_toxic_score", 0.5)
            filter_violations = insight_metadata.get("filter_violations", 0)
            violated_filter_questions: Optional[List[Tuple[str, int, str]]] = insight_metadata.get("violated_filter_questions")
            top_redflag_questions: Optional[List[Tuple[str, float, str]]] = insight_metadata.get("top_redflag_questions")
            generated_insight = insight_metadata.get("generated_insight")
            prompt_text = insight_metadata.get("prompt_text", "")
            model_name = insight_metadata.get("model_name", "")
            session_data = insight_metadata.get("session_data", {})
            
            # Format redflag questions for storage
            redflag_questions_text = ""
            redflag_ratings_text = ""
            if top_redflag_questions:
                questions = [q[0] for q in top_redflag_questions]
                ratings = [str(q[1]) for q in top_redflag_questions]
                redflag_questions_text = " | ".join(questions)
                redflag_ratings_text = " | ".join(ratings)
            
            # Format violated filter questions for storage
            violated_filter_questions_text = ""
            if violated_filter_questions:
                violated_filter_questions_text = " | ".join([q[0] for q in violated_filter_questions])
            
            # Get or create session_id based on user_id and boyfriend_name
            from src.utils.session_id_generator import get_or_create_session_id
            session_id = get_or_create_session_id(
                db_handler=db_handler,
                table_name="session_insights",
                user_id=user_id,
                boyfriend_name=bf_name,
            )
            
            # Prepare record data
            # DynamoDB requires Decimal types for numeric values, not float
            from decimal import Decimal
            timestamp = datetime.now().strftime(DATE_FORMAT)
            record_data = {
                "id": session_id,
                "timestamp": timestamp,
                "user_id": user_id,
                "name": user_name,
                "email": email or "",
                "boyfriend_name": bf_name,
                "language": language,
                "toxic_score": Decimal(str(toxic_score)),  # Use Decimal for DynamoDB
                "avg_toxic_score": Decimal(str(avg_toxic_score)),  # Use Decimal for DynamoDB
                "filter_violations": filter_violations,
                "violated_filter_questions": violated_filter_questions_text,
                "redflag_questions": redflag_questions_text,
                "redflag_ratings": redflag_ratings_text,
                "redflag_questions_count": len(top_redflag_questions) if top_redflag_questions else 0,
                "model_name": model_name,
                "prompt_text": prompt_text,
                "generated_insight": generated_insight or "",
                "insight_length": len(generated_insight) if generated_insight else 0,
                "filter_responses": str(session_data.get("filter_responses", "")),
                "redflag_responses": str(session_data.get("redflag_responses", "")),
                "toxicity_rating": session_data.get("toxicity_rating", ""),
                "feedback_rating": session_data.get("feedback_rating", ""),
                "session_start_time": session_data.get("session_start_time", ""),
                "result_start_time": session_data.get("result_start_time", ""),
            }
            
            # Save to database (CSV or DynamoDB) - update if exists
            try:
                existing = db_handler.load_table("session_insights")
                if not existing.empty:
                    # Ensure id column is numeric for proper comparison
                    import pandas as pd
                    existing["id"] = pd.to_numeric(existing["id"], errors='coerce')
                    if session_id in existing["id"].values:
                        db_handler.update_record("session_insights", {"id": session_id}, record_data)
                        print(f"[OK] Updated existing session_insights record (id: {session_id})")
                    else:
                        db_handler.add_record("session_insights", record_data)
                        print(f"[OK] Created new session_insights record (id: {session_id})")
                else:
                    db_handler.add_record("session_insights", record_data)
                    print(f"[OK] Created new session_insights record (id: {session_id})")
            except Exception as e:
                print(f"[WARNING] Error checking existing record, trying to add: {e}")
                db_handler.add_record("session_insights", record_data)
                print(f"[OK] Session insights saved to database (id: {session_id})")
            
        except Exception as e:
            print(f"[ERROR] Failed to save session insights: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
