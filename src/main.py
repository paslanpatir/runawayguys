"""Main entry point for the Streamlit survey application."""
import streamlit as st
from decimal import Decimal
from src.application.messages import Message
from src.application.session_manager import SessionManager
from src.application.survey_controller import SurveyController
from src.adapters.database.database_handler import DatabaseHandler
from src.utils.debug_helper import setup_mock_data_for_testing, is_debug_mode

# import steps
from src.application.steps.ask_language import AskLanguage
from src.application.steps.ask_user_details import AskUserDetails
from src.application.steps.ask_boyfriend_name import AskBoyfriendName
from src.application.steps.welcome import Welcome
from src.application.steps.ask_filter_questions import FilterQuestionsStep
from src.application.steps.redflag_questions_step import RedFlagQuestionsStep
from src.application.steps.gtk_questions_step import GTKQuestionsStep
from src.application.steps.toxicity_opinion_step import ToxicityOpinionStep
from src.application.steps.results_step import ResultsStep
from src.application.steps.feedback_step import FeedbackStep
from src.application.steps.report_step import ReportStep


def main(DB_READ, DB_WRITE, LLM_ENABLED=True):
    session = SessionManager()
    session.next_counter()

    # DEBUG MODE: Set up mock data to skip to results page
    if is_debug_mode() and "debug_data_set" not in st.session_state:
        setup_mock_data_for_testing()
        st.session_state.debug_data_set = True
        st.info("🔧 DEBUG MODE: Mock data loaded. Jumping to results page...")
        st.rerun()

    msg = Message(session.language)
    st.title(msg.get("survey_title"))

    # Store DB flags in session state so steps can access them
    if "db_read_allowed" not in st.session_state:
        st.session_state.db_read_allowed = DB_READ
    if "db_write_allowed" not in st.session_state:
        st.session_state.db_write_allowed = DB_WRITE
    # Store LLM flag in session state so steps can access it
    if "llm_enabled" not in st.session_state:
        st.session_state.llm_enabled = LLM_ENABLED
    
    # Load summary statistics at app start (only once)
    if "summary_loaded" not in st.session_state:
        _load_summary_statistics(DB_READ, session)
        st.session_state.summary_loaded = True

    steps = [
        AskLanguage(),
        AskUserDetails(),
        AskBoyfriendName(),
        Welcome(),
        FilterQuestionsStep(),
        RedFlagQuestionsStep(),
        GTKQuestionsStep(),
        ToxicityOpinionStep(),
        ResultsStep(DB_READ, DB_WRITE),
        FeedbackStep(DB_WRITE),
        ReportStep(),  # Now includes goodbye message
    ]

    controller = SurveyController(steps)
    # Progress bar is shown inside controller.run() before each step
    controller.run()


def _load_summary_statistics(DB_READ, session):
    """Load summary statistics from Summary_Sessions table at app start."""
    try:
        db_handler = DatabaseHandler(db_read_allowed=DB_READ)
        summary = db_handler.load_table("Summary_Sessions")
        
        if not summary.empty:
            row = summary.iloc[0]
            session.state["sum_toxic_score"] = Decimal(str(row.get("sum_toxic_score", 0)))
            session.state["max_toxic_score"] = Decimal(str(row.get("max_toxic_score", 0)))
            session.state["min_toxic_score"] = Decimal(str(row.get("min_toxic_score", 0)))
            session.state["avg_toxic_score"] = Decimal(str(row.get("avg_toxic_score", 0)))
            session.state["sum_filter_violations"] = row.get("sum_filter_violations", 0)
            session.state["avg_filter_violations"] = row.get("avg_filter_violations", 0)
            session.state["count_guys"] = row.get("count_guys", 0)
            # max_id fields no longer loaded - IDs are now hash-based and order-agnostic
            print(f"[OK] Summary statistics loaded. avg_toxic_score: {session.state['avg_toxic_score']}")
        else:
            # Initialize with defaults if table is empty
            session.state["sum_toxic_score"] = Decimal("0")
            session.state["max_toxic_score"] = Decimal("0")
            session.state["min_toxic_score"] = Decimal("1")
            session.state["avg_toxic_score"] = Decimal("0.5")
            session.state["sum_filter_violations"] = 0
            session.state["avg_filter_violations"] = 0
            session.state["count_guys"] = 0
            # max_id fields no longer initialized - IDs are now hash-based
            print("[WARNING] Summary_Sessions table is empty. Using default values.")
        
        db_handler.close()
    except (FileNotFoundError, Exception) as e:
        print(f"[WARNING] Could not load summary statistics: {e}")
        # Set defaults on error (table doesn't exist yet or other error)
        session.state["sum_toxic_score"] = Decimal("0")
        session.state["max_toxic_score"] = Decimal("0")
        session.state["min_toxic_score"] = Decimal("1")
        session.state["avg_toxic_score"] = Decimal("0.5")
        session.state["sum_filter_violations"] = 0
        session.state["avg_filter_violations"] = 0
        session.state["count_guys"] = 0
        # max_id fields no longer initialized - IDs are now hash-based
