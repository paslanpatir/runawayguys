"""Main entry point for the Streamlit survey application."""
import streamlit as st
from src.application.messages import Message
from src.application.session_manager import SessionManager
from src.application.survey_controller import SurveyController

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
from src.application.steps.goodbye_step import GoodbyeStep


def main(DB_READ, DB_WRITE):
    session = SessionManager()
    session.next_counter()

    msg = Message(session.language)
    st.title(msg.get("survey_title"))

    # Store DB flags in session state so steps can access them
    if "db_read_allowed" not in st.session_state:
        st.session_state.db_read_allowed = DB_READ
    if "db_write_allowed" not in st.session_state:
        st.session_state.db_write_allowed = DB_WRITE

    steps = [
        AskLanguage(),
        AskUserDetails(),
        AskBoyfriendName(),
        Welcome(),
        FilterQuestionsStep(),
        RedFlagQuestionsStep(),
        GTKQuestionsStep(),
        ToxicityOpinionStep(),
        ResultsStep(DB_READ),
        FeedbackStep(),
        ReportStep(),
        GoodbyeStep(DB_WRITE),
    ]

    controller = SurveyController(steps)
    # Progress bar is shown inside controller.run() before each step
    controller.run()
