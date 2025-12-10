"""Filter questions step."""
import streamlit as st
import random
from src.application.base_step import BaseStep
from src.adapters.database.database_handler import DatabaseHandler
from src.adapters.database.question_repository import QuestionRepository
from src.domain.value_objects import FilterQuestion, FilterResponse
from src.utils.utils import natural_sort_key, select_discrete_score_options


class AskFilterQuestions(BaseStep):
    name = "filter_questions"

    @staticmethod
    def get_questions(repository: QuestionRepository) -> list[FilterQuestion]:
        """Load and randomize filter questions, cache in session."""
        if "randomized_filters" not in st.session_state:
            questions = repository.get_filter_questions()
            # Randomize the list
            questions = random.sample(questions, len(questions))
            st.session_state.randomized_filters = questions
        return st.session_state.randomized_filters

    def run(self):
        import streamlit as st
        # Use DB_READ flag from session state if available, otherwise default to CSV (False)
        db_read_allowed = st.session_state.get("db_read_allowed", False)
        db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
        repository = QuestionRepository(db_handler)
        questions = self.get_questions(repository)

        if not questions:
            st.error("⚠️ No filter questions available.")
            return False  # Early return if no questions

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("filter_header"), divider=True)

        answers = {}
        violations = 0

        for index, question in enumerate(questions):
            question_text = question.get_question(language)
            upper_limit = question.upper_limit
            scoring_type = question.scoring

            opts, yes_no_opts = select_discrete_score_options(language)

            if scoring_type == "Limit":
                # Map the selected option to a score
                option_to_score = {opt: idx for idx, opt in enumerate(opts)}
                response_txt = st.select_slider(f"{question_text}", options=opts, key=f"filter_{index}")
                answer = option_to_score[response_txt]

            elif scoring_type == "YES/NO":
                response_txt = st.radio(f"{question_text}", options=yes_no_opts, key=f"radio_{index}")
                answer = 1 if response_txt == yes_no_opts[0] else 0  # Convert "Yes" or "Evet" to 1, else 0

            # Store response
            answers[f"F{question.filter_id}"] = answer
            if answer >= upper_limit:
                violations += 1

            st.divider()

        # Sort responses
        responses = dict(sorted(answers.items(), key=natural_sort_key))

        if st.button(msg.get("continue_msg")):
            # Create FilterResponse value object
            filter_response = FilterResponse(responses=responses, violations=violations)
            # Store in session state (can also store the value object)
            self.session.state["filter_responses"] = filter_response.responses
            self.session.state["filter_violations"] = filter_response.violations
            self.session.state["filter_response_obj"] = filter_response  # Store value object too
            st.rerun()

        return (
            self.session.state.get("filter_responses") is not None
            and self.session.state.get("filter_violations") is not None
        )


# Alias for backward compatibility
FilterQuestionsStep = AskFilterQuestions
