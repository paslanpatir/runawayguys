"""GetToKnow questions step."""
import streamlit as st
import ast
from src.base_step import BaseStep
from src.database_handler import DatabaseHandler


class GTKQuestionsStep(BaseStep):
    name = "gtk_questions"

    @staticmethod
    def parse_levels(levels_str):
        """Parse the Levels column string into a list of levels."""
        import pandas as pd

        if pd.isna(levels_str) or levels_str.strip() == "":
            return None
        try:
            return ast.literal_eval(levels_str)
        except (ValueError, SyntaxError):
            st.error(f"Invalid Levels format: {levels_str}")
            return None

    @staticmethod
    def get_questions(db_handler: DatabaseHandler):
        """Load GTK questions, cache in session."""
        if "gtk_questions" not in st.session_state:
            st.session_state.gtk_questions = db_handler.load_table("GetToKnowQuestions")
        return st.session_state.gtk_questions

    def run(self):
        db_handler = DatabaseHandler()
        gtk_questions = self.get_questions(db_handler)

        if gtk_questions is None or gtk_questions.empty:
            st.error("⚠️ No GTK questions available.")
            return False

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("gtk_header"), divider=True)

        responses = {}

        for index, row in gtk_questions.iterrows():
            question = row[f"Question_{language}"]
            scoring_type = row["Scoring"]
            levels = self.parse_levels(row[f"Levels_{language}"])

            if scoring_type.startswith("Range"):
                if levels:
                    options = levels
                    response = st.select_slider(question, options=options, key=f"gtk_{row['GTK_ID']}")
                else:
                    range_values = scoring_type.replace("Range(", "").replace(")", "").split("-")
                    min_value = int(range_values[0])
                    max_value = int(range_values[1])
                    options = list(range(min_value, max_value + 1))
                    response = st.select_slider(question, options=options, key=f"gtk_{row['GTK_ID']}")
            elif scoring_type == "YES/NO":
                options = msg.get("boolean_answer")
                response = st.radio(question, options=options, key=f"gtk_{row['GTK_ID']}")
            else:
                st.error(f"Unsupported scoring type: {scoring_type}")
                continue

            response_int = options.index(response) + 1
            responses[f"GTK{row['GTK_ID']}"] = response_int

            st.divider()

        if st.button(msg.get("continue_msg")):
            self.session.state["extra_questions_responses"] = responses
            st.rerun()

        return self.session.state.get("extra_questions_responses") is not None

