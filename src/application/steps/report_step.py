"""Report step - sends automatic results via email if requested."""
import streamlit as st
from decimal import Decimal
from src.application.base_step import BaseStep
from src.adapters.email.email_adapter import send_survey_report
from src.adapters.database.database_handler import DatabaseHandler
from src.utils.redflag_utils import get_violated_filter_questions
from datetime import datetime


class ReportStep(BaseStep):
    name = "report"

    def run(self):
        """
        Send automatic report via email if user requested it.
        """
        msg = self.msg
        
        email = self.session.user_details.get("email")
        
        if email:
            # Prepare session data for email (include AI insights if available and LLM is enabled)
            llm_enabled = self.session.state.get("llm_enabled", False)
            language = self.session.user_details.get("language", "EN")
            
            # Get avg_toxic_score - load from database if not in session state or if it's 0
            avg_toxic_score_decimal = self.session.state.get("avg_toxic_score")
            if avg_toxic_score_decimal is None or (isinstance(avg_toxic_score_decimal, Decimal) and avg_toxic_score_decimal == 0):
                # Load from database if not already loaded
                try:
                    db_read_allowed = self.session.state.get("db_read_allowed", False)
                    db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
                    summary = db_handler.load_table("Summary_Sessions")
                    
                    if not summary.empty:
                        row = summary.iloc[0]
                        avg_toxic_score_decimal = Decimal(str(row.get("avg_toxic_score", 0)))
                    else:
                        # Calculate from session_responses as fallback
                        session_responses = db_handler.load_table("session_responses")
                        if not session_responses.empty and "toxic_score" in session_responses.columns:
                            avg_toxic_score_decimal = Decimal(str(session_responses["toxic_score"].mean()))
                        else:
                            avg_toxic_score_decimal = Decimal("0.5")
                    
                    db_handler.close()
                except Exception as e:
                    print(f"[WARNING] Could not load avg_toxic_score from database: {e}")
                    avg_toxic_score_decimal = Decimal("0.5")
            
            # Get violated filter questions for email
            violated_filter_questions = get_violated_filter_questions(
                self.session.state.get("filter_responses", {}),
                self.session.state.get("filter_questions", []),
                language,
                use_english_for_llm=False  # Use display language for email
            )
            
            # Get category scores for email
            category_scores = None
            try:
                from src.utils.category_analysis import calculate_category_toxicity_scores
                redflag_responses = self.session.state.get("redflag_responses", {})
                redflag_questions = self.session.state.get("redflag_questions", [])
                
                if redflag_responses and redflag_questions:
                    category_scores = calculate_category_toxicity_scores(
                        redflag_responses,
                        redflag_questions,
                        language=language
                    )
            except Exception as e:
                print(f"[WARNING] Could not calculate category scores for email: {e}")
            
            # Prepare email data - send_survey_report expects user_details dict
            email_data = {
                "user_details": {
                    "name": self.session.user_details.get("name", "User"),
                    "bf_name": self.session.user_details.get("bf_name", "Your boyfriend"),
                },
                "toxic_score": float(self.session.state.get("toxic_score", 0)),
                "avg_toxic_score": float(avg_toxic_score_decimal),
                "filter_violations": self.session.state.get("filter_violations", 0),
                "violated_filter_questions": violated_filter_questions,
                "category_scores": category_scores,
            }
            
            # Include AI insights if available
            if llm_enabled:
                ai_insights = self.session.state.get("ai_insights")
                if ai_insights:
                    email_data["ai_insights"] = ai_insights
            
            # Send email
            success = send_survey_report(email, email_data, language)
            
            if success:
                report_msg = msg.get("report_sent_to_msg", email=email)
                st.toast(report_msg, icon="📧")
                self.session.state["report_sent"] = True
            else:
                st.warning("Email could not be sent. Please check your email configuration.")
                self.session.state["report_sent"] = False
        
        # Show goodbye message (merged from GoodbyeStep)
        name = self.session.user_details.get("name", "User")
        st.divider()
        st.markdown(msg.get("goodbye_message", name=name))
        st.balloons()
        
        # Show contact information
        st.divider()
        st.markdown(msg.get("contact_email_info_msg"))
        
        # Show option to start a new survey
        st.divider()
        button_text = msg.get("start_new_survey")
        if st.button(button_text):
            # Reset survey states but keep user_id and name
            self.session.reset_for_new_survey()
            st.rerun()
        
        # Don't return True immediately - stay on this page until user clicks "Start New Survey"
        return False
