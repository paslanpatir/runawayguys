"""RedFlag questions step."""
import streamlit as st
import numpy as np
import random
from decimal import Decimal
from src.application.base_step import BaseStep
from src.adapters.database.database_handler import DatabaseHandler
from src.adapters.database.question_repository import QuestionRepository
from src.domain.value_objects import RedFlagQuestion, RedFlagResponse
from src.utils.utils import natural_sort_key


class RedFlagQuestionsStep(BaseStep):
    name = "redflag_questions"

    @staticmethod
    def get_questions(repository: QuestionRepository) -> list[RedFlagQuestion]:
        """Load and randomize redflag questions, cache in session."""
        if "randomized_questions" not in st.session_state:
            questions = repository.get_redflag_questions()
            # Randomize the list
            questions = random.sample(questions, len(questions))
            st.session_state.randomized_questions = questions
        return st.session_state.randomized_questions

    def run(self):
        import streamlit as st
        # Use DB_READ flag from session state if available, otherwise default to CSV (False)
        db_read_allowed = st.session_state.get("db_read_allowed", False)
        db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
        repository = QuestionRepository(db_handler)
        questions = self.get_questions(repository)

        if not questions:
            st.error("⚠️ No redflag questions available.")
            return False

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("toxicity_header"), divider=True)

        answers = {}
        tot_score = 0
        abs_tot_score = 0
        applicable_questions = 0
        yes_no_default_score = 7

        not_applicable_msg = msg.get("not_applicable_msg")
        select_score_msg = msg.get("select_score_msg")
        select_option_msg = msg.get("select_option_msg")
        boolean_answer = msg.get("boolean_answer")

        for index, question in enumerate(questions):
            question_text = question.get_question(language).strip()
            st.markdown(f"**{index + 1}.** **{question_text}**")

            # Initialize session state for visibility
            if f"not_applicable_{index}" not in st.session_state:
                st.session_state[f"not_applicable_{index}"] = False

            # Create two columns for the checkbox and scoring options
            col1, col2 = st.columns([3, 1])

            with col2:
                not_applicable = st.checkbox(
                    not_applicable_msg,
                    key=f"not_applicable_checkbox_{index}",
                    value=st.session_state[f"not_applicable_{index}"]
                )

                if not_applicable != st.session_state[f"not_applicable_{index}"]:
                    st.session_state[f"not_applicable_{index}"] = not_applicable
                    st.rerun()

            with col1:
                if not st.session_state[f"not_applicable_{index}"]:
                    scoring_type = question.scoring
                    if scoring_type == "Range(0-10)":
                        answer = st.slider(select_score_msg, min_value=0, max_value=10, key=f"slider_{index}")
                    elif scoring_type == "YES/NO":
                        response_txt = st.radio(select_option_msg, options=boolean_answer, key=f"radio_{index}")
                        answer = yes_no_default_score if (response_txt == "Yes" or response_txt == "Evet") else 0
                    else:
                        st.error(f"Unknown scoring type: {scoring_type}")
                        answer = 0

                    answers[f"Q{question.question_id}"] = answer

                    weight = question.weight
                    tot_score += weight * answer
                    abs_tot_score += weight * (yes_no_default_score if scoring_type == "YES/NO" else 10) * (1 if weight > 0 else -1)
                    applicable_questions += 1
                else:
                    answers[f"Q{question.question_id}"] = np.nan

            st.divider()

        # Calculate the toxic score only for applicable questions
        if applicable_questions > 0:
            toxic_score = Decimal("1.0") * Decimal(str(tot_score)) / Decimal(str(abs_tot_score))
        else:
            toxic_score = Decimal("0")

        answers = dict(sorted(answers.items(), key=natural_sort_key))

        if st.button(msg.get("continue_msg")):
            # Create RedFlagResponse value object
            toxic_score_float = float(toxic_score)
            redflag_response = RedFlagResponse(responses=answers, toxic_score=toxic_score_float)
            # Store in session state
            self.session.state["redflag_responses"] = redflag_response.responses
            self.session.state["toxic_score"] = redflag_response.toxic_score
            self.session.state["redflag_response_obj"] = redflag_response  # Store value object too
            st.rerun()

        return (
            self.session.state.get("redflag_responses") is not None
            and self.session.state.get("toxic_score") is not None
        )
