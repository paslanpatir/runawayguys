import streamlit as st
from src.base_step import BaseStep
from src.database_handler import DatabaseHandler
from src.utils import natural_sort_key, select_discrete_score_options, randomize_questions


class AskFilterQuestions(BaseStep):
    name = "filter_questions"

    @staticmethod
    def get_questions(db_handler: DatabaseHandler):
        """Load and randomize filter questions, cache in session."""
        if "randomized_filters" not in st.session_state:
            data = db_handler.load_table("RedFlagFilters")
            data = randomize_questions(data)
            st.session_state.randomized_filters = data
        return st.session_state.randomized_filters

    def run(self):
        db_handler = DatabaseHandler()
        questions = self.get_questions(db_handler)

        if questions is None or questions.empty:
            st.error("⚠️ No filter questions available.")
            return False  # Early return if no questions

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("filter_header"), divider=True)

        answers = {}
        violations = 0

        for index, row in questions.iterrows():
            question = row[f"Filter_Question_{language}"]
            upper_limit = row["Upper_Limit"]
            scoring_type = row["Scoring"]

            opts, yes_no_opts = select_discrete_score_options(language)

            if scoring_type == "Limit":
                # Map the selected option to a score
                option_to_score = {opt: idx for idx, opt in enumerate(opts)}
                response_txt = st.select_slider(f"{question}", options=opts, key=f"filter_{index}")
                answer = option_to_score[response_txt]

            elif scoring_type == "YES/NO":
                response_txt = st.radio(f"{question}", options=yes_no_opts, key=f"radio_{index}")
                answer = 1 if response_txt == yes_no_opts[0] else 0  # Convert "Yes" or "Evet" to 1, else 0

            # Store response
            answers[f"F{row['Filter_ID']}"] = answer
            if answer >= upper_limit:
                violations += 1

            st.divider()

        # Sort responses
        responses = dict(sorted(answers.items(), key=natural_sort_key))

        if st.button(msg.get("continue_msg")):
            self.session.state["filter_responses"] = responses
            self.session.state["filter_violations"] = violations
            st.rerun()

        return (
            self.session.state.get("filter_responses") is not None
            and self.session.state.get("filter_violations") is not None
        )
