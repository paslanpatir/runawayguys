import streamlit as st
import uuid
from datetime import datetime


class SessionManager:
    """Wrapper around st.session_state with initialization helpers."""

    def __init__(self):
        self.state = st.session_state
        self._initialize_defaults()

    def _initialize_defaults(self):
        if "counter" not in self.state:
            self.state.counter = 0
        if "user_details" not in self.state:
            self.state.user_details = {
                "user_id": str(uuid.uuid4()),
                "name": None,
                "email": None,
                "language": None,
                "bf_name": None,
            }
        if "welcome_shown" not in self.state:
            self.state.welcome_shown = False
        if "session_start_time" not in self.state:
            self.state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "filter_responses" not in self.state:
            self.state.filter_responses = None
            self.state.filter_violations = 0
        if "redflag_responses" not in self.state:
            self.state.redflag_responses = None
            self.state.toxic_score = None
            self.state.avg_toxic = None
        if "extra_questions_responses" not in self.state:
            self.state.extra_questions_responses = None
        if "toxicity_rating" not in self.state:
            self.state.toxicity_rating = None
        if "feedback_rating" not in self.state:
            self.state.feedback_rating = None
        if "survey_completed" not in self.state:
            self.state.survey_completed = False
        if "submitted" not in self.state:
            self.state.submitted = False
        if "new_survey_opt" not in self.state:
            self.state.new_survey_opt = False

    # Convenience properties
    @property
    def user_details(self):
        return self.state.user_details

    @property
    def language(self):
        return self.user_details.get("language", "TR")

    def next_counter(self):
        self.state.counter += 1
        return self.state.counter
