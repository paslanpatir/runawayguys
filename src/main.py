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
from src.goodbye_step import GoodbyeStep


def main(DB_READ, DB_WRITE):
    session = SessionManager()
    session.next_counter()

    msg = Message(session.language)
    st.title(msg.get("survey_title"))

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
        GoodbyeStep(DB_WRITE),
    ]

    controller = SurveyController(steps)
    controller.run()
