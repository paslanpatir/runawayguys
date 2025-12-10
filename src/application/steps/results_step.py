"""Results step - displays survey results."""
import streamlit as st
import pandas as pd
from decimal import Decimal
from src.application.base_step import BaseStep
from src.adapters.database.database_handler import DatabaseHandler

# Configuration for AI insights
TOP_REDFLAG_QUESTIONS_COUNT = 5  # Number of top-rated redflag questions to include in insights
MIN_REDFLAG_RATING = 5.0  # Minimum rating (0-10) to include a question in insights


class ResultsStep(BaseStep):
    name = "results"

    def __init__(self, db_read_allowed=False):
        super().__init__()
        self.db_read_allowed = db_read_allowed

    def run(self):
        from datetime import datetime

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        if "result_start_time" not in self.session.state:
            self.session.state["result_start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Load summary data
        self._load_summary_data()

        # Show balloons when results page is displayed
        st.balloons()

        st.subheader(msg.get("result_header"), divider=True)

        self._present_result_report()

        if st.button(msg.get("survey_complete_msg")):
            self.session.state["survey_completed"] = True
            st.rerun()

        return self.session.state.get("survey_completed") is True

    def _load_summary_data(self):
        """Load summary statistics from database."""
        try:
            db_handler = DatabaseHandler(db_read_allowed=self.db_read_allowed)
            summary = db_handler.load_table("Summary_Sessions")

            if not summary.empty:
                row = summary.iloc[0]
                self.session.state["sum_toxic_score"] = Decimal(str(row.get("sum_toxic_score", 0)))
                self.session.state["max_toxic_score"] = Decimal(str(row.get("max_toxic_score", 0)))
                self.session.state["min_toxic_score"] = Decimal(str(row.get("min_toxic_score", 0)))
                self.session.state["avg_toxic_score"] = Decimal(str(row.get("avg_toxic_score", 0)))
                self.session.state["sum_filter_violations"] = row.get("sum_filter_violations", 0)
                self.session.state["avg_filter_violations"] = row.get("avg_filter_violations", 0)
                self.session.state["count_guys"] = row.get("count_guys", 0)
        except Exception as e:
            st.warning(f"Could not load summary data: {e}")
            # Set defaults
            self.session.state["avg_toxic_score"] = Decimal("0.5")
            self.session.state["avg_filter_violations"] = 0

    def _present_result_report(self):
        """Present the result report to the user."""
        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        avg_toxic_score = self.session.state.get("avg_toxic_score", Decimal("0.5"))
        toxic_score = self.session.state.get("toxic_score", 0)
        avg_filter_violations = self.session.state.get("avg_filter_violations", 0)
        filter_violations = self.session.state.get("filter_violations", 0)
        bf_name = self.session.user_details.get("bf_name", "Your boyfriend")

        if toxic_score:
            st.info(msg.get("toxic_score_info", toxic_score=round(100 * toxic_score, 1)), icon="⚡")
            if Decimal(str(toxic_score)) > avg_toxic_score:
                st.error(msg.get("red_flag_fail_msg", bf_name=bf_name))
            else:
                st.success(msg.get("red_flag_pass_msg", bf_name=bf_name))
        else:
            st.success(msg.get("red_flag_pass_msg", bf_name=bf_name))

        st.divider()

        if filter_violations:
            if filter_violations > 0:
                st.error(msg.get("filter_fail_msg", bf_name=bf_name, filter_violations=filter_violations))
        else:
            st.success(msg.get("filter_pass_msg", bf_name=bf_name))

        st.divider()

        # Try to show toxic graph
        self._show_toxic_graph()

        # Show AI-generated insights (only if LLM is enabled)
        llm_enabled = self.session.state.get("llm_enabled", False)
        if llm_enabled:
            st.divider()
            self._show_ai_insights()

    def _show_toxic_graph(self):
        """Show toxicity comparison graph using plotnine."""
        try:
            import numpy as np
            from decimal import Decimal, ROUND_HALF_UP
            from plotnine import ggplot, aes, geom_point, labs, theme_minimal

            language = self.session.user_details.get("language") or "EN"
            msg = self.msg

            db_handler = DatabaseHandler(db_read_allowed=self.db_read_allowed)
            session_responses = db_handler.load_table("session_responses")

            if session_responses.empty:
                return

            toxic_score = self.session.state.get("toxic_score", 0)
            if not toxic_score:
                return

            # Prepare the data - get last 20 entries
            temp = session_responses[["id", "toxic_score"]].tail(20).copy()

            if temp.empty:
                return

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

            guy_cnt = len(temp)

            st.markdown(msg.get("toxic_graph_guy_cnt", guy_cnt=guy_cnt))
            st.markdown(msg.get("toxic_graph_msg"))

            # Create the plot using plotnine
            from plotnine import theme_minimal

            p = (
                ggplot(temp, aes(x="index", y="toxic_score", color="guys"))
                + geom_point()  # Scatter plot with color based on frequency
                + labs(
                    title="",
                    x=msg.get("toxic_graph_x"),
                    y=msg.get("toxic_graph_y"),
                )
                + theme_minimal()
            )

            # Convert the plotnine plot to a matplotlib figure and display
            fig = p.draw()
            st.pyplot(fig)

        except ImportError:
            st.warning("plotnine is not installed. Install it with: pip install plotnine")
        except Exception as e:
            # Silently fail if graph can't be shown
            st.debug(f"Could not show graph: {e}")

    def _show_ai_insights(self):
        """Generate and display AI insights."""
        # Check if LLM is enabled
        llm_enabled = self.session.state.get("llm_enabled", False)
        if not llm_enabled:
            # LLM feature is disabled, skip insights
            return

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        # Check if insights already generated
        if "ai_insights" not in self.session.state:
            # Generate insights
            spinner_text = msg.get("generating_insights_msg") if msg.texts.get("generating_insights_msg") else "Generating personalized insights..."
            with st.spinner(spinner_text):
                from src.services.insight_service import InsightService
                from src.utils.redflag_utils import get_top_redflag_questions, get_violated_filter_questions
                from src.adapters.database.database_handler import DatabaseHandler
                from src.adapters.database.question_repository import QuestionRepository
                from decimal import Decimal
                
                insight_service = InsightService(enabled=True)
                user_name = self.session.user_details.get("name", "User")
                bf_name = self.session.user_details.get("bf_name", "Your boyfriend")
                user_id = self.session.user_details.get("user_id", "unknown")
                email = self.session.user_details.get("email")
                toxic_score = self.session.state.get("toxic_score", 0)
                filter_violations = self.session.state.get("filter_violations", 0)
                
                # Get avg_toxic_score (convert from Decimal to float)
                avg_toxic_score_decimal = self.session.state.get("avg_toxic_score", Decimal("0.5"))
                if isinstance(avg_toxic_score_decimal, Decimal):
                    avg_toxic_score = float(avg_toxic_score_decimal)
                else:
                    avg_toxic_score = float(avg_toxic_score_decimal) if avg_toxic_score_decimal else 0.5
                
                # Get top redflag questions for insights
                top_redflag_questions = None
                redflag_responses = self.session.state.get("redflag_responses")
                questions = self.session.state.get("randomized_questions")
                
                if redflag_responses and questions:
                    # Get top N questions with rating >= minimum threshold
                    top_redflag_questions = get_top_redflag_questions(
                        redflag_responses=redflag_responses,
                        questions=questions,
                        language=language,
                        top_n=TOP_REDFLAG_QUESTIONS_COUNT,
                        min_rating=MIN_REDFLAG_RATING,
                    )
                
                # Get violated filter questions
                violated_filter_questions = None
                filter_responses = self.session.state.get("filter_responses", {})
                filter_questions = self.session.state.get("randomized_filters")
                
                # If filter questions not in session, load from database
                if not filter_questions and filter_responses:
                    db_read_allowed = self.session.state.get("db_read_allowed", False)
                    db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
                    repository = QuestionRepository(db_handler)
                    filter_questions = repository.get_filter_questions()
                    # Cache them for potential future use
                    self.session.state.randomized_filters = filter_questions
                
                if filter_responses and filter_questions:
                    violated_filter_questions = get_violated_filter_questions(
                        filter_responses=filter_responses,
                        questions=filter_questions,
                        language=language,
                    )
                
                # Prepare session data for logging
                session_data_for_log = {
                    "session_id": user_id,
                    "avg_toxic_score": str(avg_toxic_score),
                    "filter_responses": filter_responses,
                    "redflag_responses": self.session.state.get("redflag_responses", {}),
                    "toxicity_rating": self.session.state.get("toxicity_rating"),
                    "feedback_rating": self.session.state.get("feedback_rating"),
                    "session_start_time": self.session.state.get("session_start_time", ""),
                    "result_start_time": self.session.state.get("result_start_time", ""),
                }
                
                insights = insight_service.generate_survey_insights(
                    user_name=user_name,
                    bf_name=bf_name,
                    toxic_score=toxic_score,
                    avg_toxic_score=avg_toxic_score,
                    filter_violations=filter_violations,
                    violated_filter_questions=violated_filter_questions,
                    language=language,
                    top_redflag_questions=top_redflag_questions,
                    user_id=user_id,
                    email=email,
                    session_data=session_data_for_log,
                )
                
                self.session.state["ai_insights"] = insights
                insight_service.close()

        # Display insights
        insights = self.session.state.get("ai_insights")
        if insights:
            header_text = msg.get("insights_header") if msg.texts.get("insights_header") else "AI-Generated Insights"
            st.subheader(header_text)
            st.info(insights)
        else:
            unavailable_text = msg.get("insights_unavailable_msg") if msg.texts.get("insights_unavailable_msg") else "AI insights are not available. LLM API is not configured."
            st.info(unavailable_text)

