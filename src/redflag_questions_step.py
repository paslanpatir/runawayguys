"""RedFlag questions step."""
import streamlit as st
import numpy as np
from decimal import Decimal
from src.base_step import BaseStep
from src.database_handler import DatabaseHandler
from src.utils import natural_sort_key, randomize_questions


class RedFlagQuestionsStep(BaseStep):
    name = "redflag_questions"

    @staticmethod
    def get_questions(db_handler: DatabaseHandler):
        """Load and randomize redflag questions, cache in session."""
        if "randomized_questions" not in st.session_state:
            data = db_handler.load_table("RedFlagQuestions")
            data = randomize_questions(data)
            st.session_state.randomized_questions = data
        return st.session_state.randomized_questions

    def run(self):
        import streamlit as st
        # Use DB_READ flag from session state if available, otherwise default to CSV (False)
        db_read_allowed = st.session_state.get("db_read_allowed", False)
        db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
        questions = self.get_questions(db_handler)

        if questions is None or questions.empty:
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

        for index, row in questions.iterrows():
            question = row[f"Question_{language}"].strip()
            st.markdown(f"**{index + 1}.** **{question}**")

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
                    scoring_type = row["Scoring"]
                    if scoring_type == "Range(0-10)":
                        answer = st.slider(select_score_msg, min_value=0, max_value=10, key=f"slider_{index}")
                    elif scoring_type == "YES/NO":
                        response_txt = st.radio(select_option_msg, options=boolean_answer, key=f"radio_{index}")
                        answer = yes_no_default_score if (response_txt == "Yes" or response_txt == "Evet") else 0
                    else:
                        st.error(f"Unknown scoring type: {scoring_type}")
                        answer = 0

                    answers[f"Q{row['ID']}"] = answer

                    weight = row["Weight"]
                    tot_score += weight * answer
                    abs_tot_score += weight * (yes_no_default_score if scoring_type == "YES/NO" else 10) * (1 if weight > 0 else -1)
                    applicable_questions += 1
                else:
                    answers[f"Q{row['ID']}"] = np.nan

            st.divider()

        # Calculate the toxic score only for applicable questions
        if applicable_questions > 0:
            toxic_score = Decimal("1.0") * tot_score / abs_tot_score
        else:
            toxic_score = 0

        answers = dict(sorted(answers.items(), key=natural_sort_key))

        if st.button(msg.get("continue_msg")):
            self.session.state["redflag_responses"] = answers
            self.session.state["toxic_score"] = float(toxic_score)
            st.rerun()

        return (
            self.session.state.get("redflag_responses") is not None
            and self.session.state.get("toxic_score") is not None
        )

