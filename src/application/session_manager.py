"""Session state management for Streamlit."""
import streamlit as st
import uuid
from datetime import datetime
from src.utils.constants import DATE_FORMAT


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
            self.state.session_start_time = datetime.now().strftime(DATE_FORMAT)
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
        if "report_sent" not in self.state:
            self.state.report_sent = False

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

    def reset_for_new_survey(self):
        """Reset survey-specific states while keeping user_id and name."""
        # Keep user_id and name
        user_id = self.state.user_details.get("user_id")
        name = self.state.user_details.get("name")
        email = self.state.user_details.get("email")
        language = self.state.user_details.get("language")
        
        # Reset survey-specific states
        self.state.welcome_shown = False
        self.state.session_start_time = datetime.now().strftime(DATE_FORMAT)
        self.state.filter_responses = None
        self.state.filter_violations = 0
        self.state.redflag_responses = None
        self.state.toxic_score = None
        self.state.avg_toxic = None
        self.state.extra_questions_responses = None
        self.state.toxicity_rating = None
        self.state.feedback_rating = None
        self.state.survey_completed = False
        self.state.submitted = False
        self.state.report_sent = False
        
        # Reset boyfriend-specific data
        self.state.user_details["bf_name"] = None
        
        # Reset cached questions
        if "randomized_filters" in self.state:
            del self.state.randomized_filters
        if "randomized_questions" in self.state:
            del self.state.randomized_questions
        if "gtk_questions" in self.state:
            del self.state.gtk_questions
        
        # Reset value objects
        if "filter_response_obj" in self.state:
            del self.state.filter_response_obj
        if "redflag_response_obj" in self.state:
            del self.state.redflag_response_obj
        if "gtk_response_obj" in self.state:
            del self.state.gtk_response_obj
        
        # Reset AI insights
        if "ai_insights" in self.state:
            del self.state.ai_insights
        if "ai_insights_generating" in self.state:
            del self.state.ai_insights_generating
        if "ai_insights_shown" in self.state:
            del self.state.ai_insights_shown
        
        # Reset data saving flags so next survey can save
        if "data_saved" in self.state:
            self.state.data_saved = False
        if "main_data_saved" in self.state:
            self.state.main_data_saved = False
        if "feedback_saved" in self.state:
            self.state.feedback_saved = False
        
        # Reset timing flags
        if "result_start_time" in self.state:
            del self.state.result_start_time
        
        # Reset UI flags
        if "results_balloons_shown" in self.state:
            del self.state.results_balloons_shown
        
        # Reset step counter to start from boyfriend name step (step 2)
        # Step 0: Language, Step 1: User Details, Step 2: Boyfriend Name
        # We keep language and user details, so we start from boyfriend name
        self.state.current_step = 2

