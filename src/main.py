import streamlit as st
from src.messages import Message
from src.session_manager import SessionManager
from src.survey_controller import SurveyController

# import steps
from src.ask_language import AskLanguage
from src.ask_user_details import AskUserDetails
from src.ask_boyfriend_name import AskBoyfriendName
from src.welcome import Welcome
from src.filter_questions_step import FilterQuestionsStep
from src.redflag_questions_step import RedFlagQuestionsStep
from src.gtk_questions_step import GTKQuestionsStep
from src.toxicity_opinion_step import ToxicityOpinionStep
from src.results_step import ResultsStep
from src.feedback_step import FeedbackStep
from src.report_step import ReportStep
from src.goodbye_step import GoodbyeStep


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
    controller.run()
