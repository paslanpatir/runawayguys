"""Report step - sends automatic results via email if requested."""
import streamlit as st
import io
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
            
            session_data = {
                "user_details": self.session.user_details,
                "toxic_score": self.session.state.get("toxic_score", 0),
                "avg_toxic_score": avg_toxic_score,
                "filter_violations": self.session.state.get("filter_violations", 0),
                "violated_filter_questions": violated_filter_questions,
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
    
    def _generate_toxic_plot_image(self) -> bytes:
        """Generate toxic plot as PNG image bytes for email embedding."""
        try:
            import numpy as np
            import pandas as pd
            from decimal import Decimal, ROUND_HALF_UP
            from plotnine import ggplot, aes, geom_point, labs, theme_minimal
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            
            db_read_allowed = self.session.state.get("db_read_allowed", False)
            db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
            session_responses = db_handler.load_table("session_responses")
            
            print(f"[DEBUG] Graph generation - session_responses empty: {session_responses.empty}")
            
            if session_responses.empty:
                print("[WARNING] session_responses table is empty, cannot generate graph")
                return None
            
            toxic_score = self.session.state.get("toxic_score", 0)
            print(f"[DEBUG] Graph generation - toxic_score: {toxic_score}")
            if not toxic_score:
                print("[WARNING] toxic_score is 0 or None, cannot generate graph")
                return None
            
            # Prepare the data - get last 20 entries
            if "id" not in session_responses.columns or "toxic_score" not in session_responses.columns:
                print(f"[WARNING] Required columns not found. Available columns: {list(session_responses.columns)}")
                return None
            
            temp = session_responses[["id", "toxic_score"]].tail(20).copy()
            
            if temp.empty:
                print("[WARNING] No data in temp dataframe after filtering")
                return None
            
            # Add current user's score with id=0 as marker
            temp.loc[-1] = [0, toxic_score]
            boyfriend_name = self.session.user_details.get("bf_name", "Your guy")
            
            # Create flag column and guys column
            temp.loc[:, "FLAG"] = np.where(temp["id"] == 0, 1, 0)
            temp.loc[:, "guys"] = "others"
            temp.loc[temp["FLAG"] == 1, "guys"] = boyfriend_name
            
            # Sort by toxic_score and reset index
            temp = temp.sort_values("toxic_score").reset_index(drop=True).reset_index()
            
            # Round toxic_score to 2 decimal places
            if "toxic_score" in temp.columns:
                temp["toxic_score"] = temp["toxic_score"].apply(
                    lambda x: Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    if pd.notna(x) else Decimal("0")
                )
            
            # Create the plot using plotnine
            language = self.session.user_details.get("language", "EN")
            msg = self.msg
            
            print(f"[DEBUG] Graph generation - Creating plot with {len(temp)} data points")
            
            p = (
                ggplot(temp, aes(x="index", y="toxic_score", color="guys"))
                + geom_point()
                + labs(
                    title="",
                    x=msg.get("toxic_graph_x"),
                    y=msg.get("toxic_graph_y"),
                )
                + theme_minimal()
            )
            
            # Convert plotnine plot to matplotlib figure
            fig = p.draw()
            
            if fig is None:
                print("[WARNING] Failed to draw plotnine figure")
                return None
            
            # Save to bytes buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            image_bytes = buf.read()
            buf.close()
            plt.close(fig)  # Close figure to free memory
            
            print(f"[DEBUG] Graph generation - Successfully generated image, size: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Could not generate toxic plot image for email: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return None

