"""GetToKnow questions step."""
import streamlit as st
from src.application.base_step import BaseStep
from src.adapters.database.database_handler import DatabaseHandler
from src.adapters.database.question_repository import QuestionRepository
from src.domain.value_objects import GTKQuestion, GTKResponse


class GTKQuestionsStep(BaseStep):
    name = "gtk_questions"

    @staticmethod
    def get_questions(repository: QuestionRepository) -> list[GTKQuestion]:
        """Load GTK questions, cache in session."""
        if "gtk_questions" not in st.session_state:
            questions = repository.get_gtk_questions()
            st.session_state.gtk_questions = questions
        return st.session_state.gtk_questions

    def run(self):
        import streamlit as st
        # Use DB_READ flag from session state if available, otherwise default to CSV (False)
        db_read_allowed = st.session_state.get("db_read_allowed", False)
        db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
        repository = QuestionRepository(db_handler)
        gtk_questions = self.get_questions(repository)

        if not gtk_questions:
            st.error("⚠️ No GTK questions available.")
            return False

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("gtk_header"), divider=True)

        responses = {}

        for question in gtk_questions:
            question_text = question.get_question(language)
            scoring_type = question.scoring
            levels = question.get_levels(language)

            if scoring_type.startswith("Range"):
                if levels:
                    options = levels
                    response = st.select_slider(question_text, options=options, key=f"gtk_{question.gtk_id}")
                else:
                    range_values = scoring_type.replace("Range(", "").replace(")", "").split("-")
                    min_value = int(range_values[0])
                    max_value = int(range_values[1])
                    options = list(range(min_value, max_value + 1))
                    response = st.select_slider(question_text, options=options, key=f"gtk_{question.gtk_id}")
            elif scoring_type == "YES/NO":
                options = msg.get("boolean_answer")
                response = st.radio(question_text, options=options, key=f"gtk_{question.gtk_id}")
            else:
                st.error(f"Unsupported scoring type: {scoring_type}")
                continue

            response_int = options.index(response) + 1
            responses[f"GTK{question.gtk_id}"] = response_int

            st.divider()

        if st.button(msg.get("continue_msg")):
            # Create GTKResponse value object
            gtk_response = GTKResponse(responses=responses)
            # Store in session state
            self.session.state["extra_questions_responses"] = gtk_response.responses
            self.session.state["gtk_response_obj"] = gtk_response  # Store value object too
            st.rerun()

        return self.session.state.get("extra_questions_responses") is not None
