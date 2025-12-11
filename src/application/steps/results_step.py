"""Results step - displays survey results."""
import streamlit as st
import pandas as pd
from decimal import Decimal
from src.application.base_step import BaseStep
from src.adapters.database.database_handler import DatabaseHandler
from src.domain.value_objects import (
    SessionResponse,
    GTKResponseRecord,
    ToxicityRatingRecord,
    UserDetails,
)
from src.utils.utils import safe_decimal
from datetime import datetime

# Configuration for AI insights
TOP_REDFLAG_QUESTIONS_COUNT = 5  # Number of top-rated redflag questions to include in insights
MIN_REDFLAG_RATING = 5.0  # Minimum rating (0-10) to include a question in insights


class ResultsStep(BaseStep):
    name = "results"

    def __init__(self, db_read_allowed=False, db_write_allowed=False):
        super().__init__()
        self.db_read_allowed = db_read_allowed
        self.db_write_allowed = db_write_allowed

    def run(self):
        from datetime import datetime

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        if "result_start_time" not in self.session.state:
            self.session.state["result_start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Load summary data
        self._load_summary_data()

        # Show balloons only once when results page is first displayed
        if "results_balloons_shown" not in self.session.state:
            st.balloons()
            self.session.state["results_balloons_shown"] = True

        st.subheader(msg.get("result_header"), divider=True)

        self._present_result_report()
        
        # Save main data to database after showing results (only once)
        if not self.session.state.get("main_data_saved", False):
            self._save_main_data()
            self.session.state["main_data_saved"] = True
            st.success(self.msg.get("response_saved_msg"))

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

        # Show category-based toxicity radar chart
        st.divider()
        self._show_category_radar_chart()

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

    def _show_category_radar_chart(self):
        """Show category-based toxicity radar chart using matplotlib."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from src.utils.category_analysis import calculate_category_toxicity_scores
            from src.adapters.database.question_repository import QuestionRepository

            language = self.session.user_details.get("language") or "EN"
            msg = self.msg
            bf_name = self.session.user_details.get("bf_name", "Your boyfriend")

            # Get redflag responses and questions
            redflag_responses = self.session.state.get("redflag_responses")
            if not redflag_responses:
                return

            # Load questions from repository
            questions = self.session.state.get("randomized_questions")
            db_read_allowed = self.session.state.get("db_read_allowed", False)
            db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
            
            if not questions:
                repository = QuestionRepository(db_handler)
                questions = repository.get_redflag_questions()

            if not questions:
                return

            # Load category names from RedFlagCategories table based on language
            category_names_map = {}
            try:
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
                print(f"[WARNING] Could not load category names: {e}")
            
            # Calculate category scores with language-specific names
            category_scores = calculate_category_toxicity_scores(
                redflag_responses, questions, language, category_names_map
            )
            
            # Debug: Print category scores (ASCII-safe - only count)
            print(f"[DEBUG] Number of categories with scores: {len(category_scores)}")
            
            if not category_scores:
                st.warning(msg.get("no_category_data_msg"))
                print("[DEBUG] No category scores found. Checking questions...")
                # Debug: Check if questions have category_name (ASCII-safe)
                categories_count = 0
                for q in questions[:5]:  # Check first 5 questions
                    if q.category_id:
                        categories_count += 1
                print(f"[DEBUG] Questions with category_id (first 5): {categories_count}")
                return

            # Prepare data for radar chart
            categories = list(category_scores.keys())
            scores = [score for score, _ in category_scores.values()]
            
            # Number of categories
            N = len(categories)
            if N < 3:  # Need at least 3 categories for a meaningful radar chart
                st.info(msg.get("no_category_data_msg"))
                return

            # Compute angle for each category
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Complete the circle

            # Prepare scores (add first value at the end to close the circle)
            scores_plot = scores + [scores[0]]

            # Add title
            st.subheader(msg.get("category_toxicity_header"))
            st.caption(msg.get("category_toxicity_description", bf_name=bf_name))

            # Create the figure using matplotlib (smaller size)
            fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(projection='polar'))
            
            # Plot the data
            ax.plot(angles, scores_plot, 'o-', linewidth=2, label=bf_name, color='darkblue')
            ax.fill(angles, scores_plot, alpha=0.25, color='lightblue')
            
            # Add category labels (smaller font for better fit)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=9)
            
            # Set y-axis limits (0-10 scale)
            ax.set_ylim(0, 10)
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=8)
            ax.grid(True)

            # Display the chart
            st.pyplot(fig)
            plt.close(fig)

        except ImportError as e:
            st.warning(f"matplotlib is not installed. Install it with: pip install matplotlib. Error: {e}")
        except Exception as e:
            # Show error to user for debugging
            st.error(f"Could not show category radar chart: {e}")
            import traceback
            print(f"[ERROR] Category radar chart error: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            st.exception(e)  # Show full exception in Streamlit

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
                    # Always use English versions for LLM (better performance)
                    top_redflag_questions = get_top_redflag_questions(
                        redflag_responses=redflag_responses,
                        questions=questions,
                        language=language,  # For logging/display
                        top_n=TOP_REDFLAG_QUESTIONS_COUNT,
                        min_rating=MIN_REDFLAG_RATING,
                        use_english_for_llm=True,  # Always use English for LLM
                    )
                
                # Get violated filter questions
                violated_filter_questions = None
                filter_responses = self.session.state.get("filter_responses")
                
                # Handle None case - convert to empty dict
                if filter_responses is None:
                    filter_responses = {}
                
                filter_questions = self.session.state.get("randomized_filters")
                
                # Debug: Print filter responses and questions
                print(f"[DEBUG] Filter responses: {filter_responses}")
                print(f"[DEBUG] Filter responses type: {type(filter_responses)}")
                print(f"[DEBUG] Filter questions in session: {filter_questions is not None}")
                if filter_questions:
                    print(f"[DEBUG] Filter questions count: {len(filter_questions)}")
                
                # If filter questions not in session, load from database
                if not filter_questions and filter_responses:
                    db_read_allowed = self.session.state.get("db_read_allowed", False)
                    db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
                    repository = QuestionRepository(db_handler)
                    filter_questions = repository.get_filter_questions()
                    # Cache them for potential future use
                    if filter_questions:
                        self.session.state.randomized_filters = filter_questions
                        print(f"[DEBUG] Loaded {len(filter_questions)} filter questions from database")
                
                if filter_responses and filter_questions:
                    print(f"[DEBUG] Getting violated filter questions from {len(filter_responses)} responses and {len(filter_questions)} questions")
                    # Always use English versions for LLM (better performance)
                    violated_filter_questions = get_violated_filter_questions(
                        filter_responses=filter_responses,
                        questions=filter_questions,
                        language=language,  # For logging/display
                        use_english_for_llm=True,  # Always use English for LLM
                    )
                    print(f"[DEBUG] Found {len(violated_filter_questions) if violated_filter_questions else 0} violated filter questions")
                    if violated_filter_questions:
                        # Print only filter IDs to avoid encoding issues with Turkish characters
                        violated_ids = [q[2] for q in violated_filter_questions]  # q[2] is filter_id
                        print(f"[DEBUG] Violated filter IDs: {violated_ids}")
                else:
                    print(f"[DEBUG] Cannot get violated filter questions: filter_responses={bool(filter_responses)}, filter_questions={bool(filter_questions)}")
                
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
            
            # Display disclaimer note with rainbow emoji
            disclaimer_text = msg.get("insights_disclaimer") if msg.texts.get("insights_disclaimer") else "**Note:** This is a simple analysis and may be wrong. Please do not take it seriously, just take it into account simply."
            st.markdown(f":rainbow[{disclaimer_text}]")
            
            st.info(insights)
        else:
            unavailable_text = msg.get("insights_unavailable_msg") if msg.texts.get("insights_unavailable_msg") else "AI insights are not available. LLM API is not configured."
            st.info(unavailable_text)
    
    def _save_main_data(self):
        """Save main session data to database (CSV or DynamoDB based on flag)."""
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
            
            # Update Summary_Sessions table after saving all data
            if self.session.state.get("redflag_responses") and self.session.state.get("filter_responses"):
                self._update_summary_statistics(db_handler)
            
            # Save session insights if available
            if self.session.state.get("insight_metadata"):
                self._save_session_insights(db_handler)
            
            db_handler.close()
        except Exception as e:
            st.error(self.msg.get("response_error_msg", e=str(e)))
    
    def _save_session_response(self, db_handler):
        """Save main session response data using SessionResponse value object."""
        from src.utils.session_id_generator import generate_session_id
        
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )
        
        session_id = generate_session_id(user_details.user_id, user_details.bf_name)
        session_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        try:
            existing = db_handler.load_table("session_responses")
            if not existing.empty:
                existing["id"] = pd.to_numeric(existing["id"], errors='coerce')
                if session_id in existing["id"].values:
                    db_handler.update_record("session_responses", {"id": session_id}, record_dict)
                    print(f"[OK] Updated existing session_response record (id: {session_id})")
                else:
                    db_handler.add_record("session_responses", record_dict)
                    print(f"[OK] Created new session_response record (id: {session_id})")
            else:
                db_handler.add_record("session_responses", record_dict)
                print(f"[OK] Created new session_response record (id: {session_id})")
        except Exception:
            db_handler.add_record("session_responses", record_dict)
    
    def _save_gtk_response(self, db_handler):
        """Save GetToKnow questions responses using GTKResponseRecord value object."""
        from src.utils.session_id_generator import generate_session_id
        
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )
        
        session_id = generate_session_id(user_details.user_id, user_details.bf_name)
        
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
            if not existing.empty:
                existing["id"] = pd.to_numeric(existing["id"], errors='coerce')
                if session_id in existing["id"].values:
                    db_handler.update_record("session_gtk_responses", {"id": session_id}, record_dict)
                    print(f"[OK] Updated existing gtk_response record (id: {session_id})")
                else:
                    db_handler.add_record("session_gtk_responses", record_dict)
                    print(f"[OK] Created new gtk_response record (id: {session_id})")
            else:
                db_handler.add_record("session_gtk_responses", record_dict)
                print(f"[OK] Created new gtk_response record (id: {session_id})")
        except Exception:
            db_handler.add_record("session_gtk_responses", record_dict)
    
    def _save_toxicity_rating(self, db_handler):
        """Save toxicity rating using ToxicityRatingRecord value object."""
        from src.utils.session_id_generator import generate_session_id
        
        user_details = UserDetails(
            user_id=self.session.user_details["user_id"],
            name=self.session.user_details["name"],
            email=self.session.user_details["email"],
            language=self.session.user_details["language"],
            bf_name=self.session.user_details["bf_name"],
        )
        
        session_id = generate_session_id(user_details.user_id, user_details.bf_name)
        
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
            if not existing.empty:
                existing["id"] = pd.to_numeric(existing["id"], errors='coerce')
                if session_id in existing["id"].values:
                    db_handler.update_record("session_toxicity_rating", {"id": session_id}, record_dict)
                    print(f"[OK] Updated existing toxicity_rating record (id: {session_id})")
                else:
                    db_handler.add_record("session_toxicity_rating", record_dict)
                    print(f"[OK] Created new toxicity_rating record (id: {session_id})")
            else:
                db_handler.add_record("session_toxicity_rating", record_dict)
                print(f"[OK] Created new toxicity_rating record (id: {session_id})")
        except Exception:
            db_handler.add_record("session_toxicity_rating", record_dict)
    
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
            
            # Track max IDs for statistics purposes (not used for ID generation - IDs are now hash-based)
            max_id_session_responses = int(self.session.state.get("max_id_session_responses", 0))
            max_id_gtk_responses = int(self.session.state.get("max_id_gtk_responses", 0))
            max_id_feedback = int(self.session.state.get("max_id_feedback", 0))
            max_id_session_toxicity_rating = int(self.session.state.get("max_id_session_toxicity_rating", 0))
            
            # Update max IDs by checking actual records (for statistics)
            try:
                session_responses = db_handler.load_table("session_responses")
                if not session_responses.empty and "id" in session_responses.columns:
                    session_responses["id"] = pd.to_numeric(session_responses["id"], errors='coerce')
                    max_id_session_responses = max(max_id_session_responses, int(session_responses["id"].max()))
            except:
                pass
            
            try:
                gtk_responses = db_handler.load_table("session_gtk_responses")
                if not gtk_responses.empty and "id" in gtk_responses.columns:
                    gtk_responses["id"] = pd.to_numeric(gtk_responses["id"], errors='coerce')
                    max_id_gtk_responses = max(max_id_gtk_responses, int(gtk_responses["id"].max()))
            except:
                pass
            
            try:
                feedback = db_handler.load_table("session_feedback")
                if not feedback.empty and "id" in feedback.columns:
                    feedback["id"] = pd.to_numeric(feedback["id"], errors='coerce')
                    max_id_feedback = max(max_id_feedback, int(feedback["id"].max()))
            except:
                pass
            
            try:
                toxicity_rating = db_handler.load_table("session_toxicity_rating")
                if not toxicity_rating.empty and "id" in toxicity_rating.columns:
                    toxicity_rating["id"] = pd.to_numeric(toxicity_rating["id"], errors='coerce')
                    max_id_session_toxicity_rating = max(max_id_session_toxicity_rating, int(toxicity_rating["id"].max()))
            except:
                pass
            
            last_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare update dictionary - DynamoDB requires Decimal types
            update_dict = {
                "sum_toxic_score": sum_toxic_score,
                "max_toxic_score": max_toxic_score,
                "min_toxic_score": min_toxic_score,
                "avg_toxic_score": avg_toxic_score,
                "sum_filter_violations": sum_filter_violations,
                "avg_filter_violations": avg_filter_violations,
                "count_guys": count_guys,
                "max_id_session_responses": max_id_session_responses,
                "max_id_gtk_responses": max_id_gtk_responses,
                "max_id_feedback": max_id_feedback,
                "max_id_session_toxicity_rating": max_id_session_toxicity_rating,
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
            self.session.state["max_id_session_responses"] = max_id_session_responses
            self.session.state["max_id_gtk_responses"] = max_id_gtk_responses
            self.session.state["max_id_feedback"] = max_id_feedback
            self.session.state["max_id_session_toxicity_rating"] = max_id_session_toxicity_rating
            
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
            from src.utils.session_id_generator import generate_session_id
            
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
            
            session_id = generate_session_id(user_id, bf_name)

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
            
            # Prepare record data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

