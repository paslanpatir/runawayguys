"""Report step - sends automatic results via email if requested."""
import streamlit as st
from decimal import Decimal
from src.application.base_step import BaseStep
from src.adapters.email.email_adapter import send_survey_report
from src.adapters.database.database_handler import DatabaseHandler
from src.utils.redflag_utils import get_violated_filter_questions


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
                        # If avg_toxic_score is 0, try to calculate from session_responses
                        if avg_toxic_score_decimal == 0:
                            print("[DEBUG] avg_toxic_score is 0 in Summary_Sessions, calculating from session_responses")
                            session_responses = db_handler.load_table("session_responses")
                            if not session_responses.empty and "toxic_score" in session_responses.columns:
                                avg_toxic_score_decimal = Decimal(str(session_responses["toxic_score"].mean()))
                                print(f"[DEBUG] Calculated avg_toxic_score from session_responses: {avg_toxic_score_decimal}")
                            else:
                                avg_toxic_score_decimal = Decimal("0.5")
                        self.session.state["avg_toxic_score"] = avg_toxic_score_decimal
                    else:
                        # Summary_Sessions is empty, try to calculate from session_responses
                        print("[DEBUG] Summary_Sessions is empty, calculating avg_toxic_score from session_responses")
                        session_responses = db_handler.load_table("session_responses")
                        if not session_responses.empty and "toxic_score" in session_responses.columns:
                            avg_toxic_score_decimal = Decimal(str(session_responses["toxic_score"].mean()))
                            print(f"[DEBUG] Calculated avg_toxic_score from session_responses: {avg_toxic_score_decimal}")
                        else:
                            avg_toxic_score_decimal = Decimal("0.5")
                        self.session.state["avg_toxic_score"] = avg_toxic_score_decimal
                except Exception as e:
                    print(f"[WARNING] Could not load avg_toxic_score from database: {e}")
                    avg_toxic_score_decimal = Decimal("0.5")
                    self.session.state["avg_toxic_score"] = avg_toxic_score_decimal
            else:
                # Use existing value from session state
                avg_toxic_score_decimal = avg_toxic_score_decimal if isinstance(avg_toxic_score_decimal, Decimal) else Decimal(str(avg_toxic_score_decimal))
            
            # Convert to float
            if isinstance(avg_toxic_score_decimal, Decimal):
                avg_toxic_score = float(avg_toxic_score_decimal)
            else:
                avg_toxic_score = float(avg_toxic_score_decimal) if avg_toxic_score_decimal else 0.5
            
            print(f"[DEBUG] Email - avg_toxic_score: {avg_toxic_score}")
            
            # Get violated filter questions
            violated_filter_questions = None
            filter_responses = self.session.state.get("filter_responses", {})
            filter_questions = self.session.state.get("randomized_filters")
            
            if filter_responses and filter_questions:
                violated_filter_questions = get_violated_filter_questions(
                    filter_responses=filter_responses,
                    questions=filter_questions,
                    language=language,
                )
            
            # Calculate category scores for email
            category_scores = None
            redflag_responses = self.session.state.get("redflag_responses")
            questions = self.session.state.get("randomized_questions")
            
            if redflag_responses and questions:
                from src.utils.category_analysis import calculate_category_toxicity_scores
                from src.adapters.database.question_repository import QuestionRepository
                
                # Load category names from RedFlagCategories table based on language
                category_names_map = {}
                try:
                    db_read_allowed = self.session.state.get("db_read_allowed", False)
                    db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
                    categories_df = db_handler.load_table("RedFlagCategories")
                    if not categories_df.empty:
                        for _, row in categories_df.iterrows():
                            cat_id = int(row["Category_ID"])
                            if language == "TR":
                                cat_name = str(row.get("Category_Name_TR", ""))
                            else:
                                cat_name = str(row.get("Category_Name_EN", ""))
                            if cat_name:
                                category_names_map[cat_id] = cat_name
                except Exception as e:
                    print(f"[WARNING] Could not load category names for email: {e}")
                
                # Calculate category scores
                category_scores = calculate_category_toxicity_scores(
                    redflag_responses, questions, language, category_names_map
                )
            
            session_data = {
                "user_details": self.session.user_details,
                "toxic_score": self.session.state.get("toxic_score", 0),
                "avg_toxic_score": avg_toxic_score,
                "filter_violations": self.session.state.get("filter_violations", 0),
                "violated_filter_questions": violated_filter_questions,
                "category_scores": category_scores,  # Add category scores
            }
            # Only include insights if LLM is enabled
            if llm_enabled:
                session_data["ai_insights"] = self.session.state.get("ai_insights")
            
            # Send email
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

