"""Results step - displays survey results."""
import streamlit as st
from decimal import Decimal
from src.base_step import BaseStep
from src.database_handler import DatabaseHandler


class ResultsStep(BaseStep):
    name = "results"

    def __init__(self, db_read_allowed=False):
        super().__init__()
        self.db_read_allowed = db_read_allowed

    def run(self):
        from datetime import datetime

        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        if "result_start_time" not in self.session.state:
            self.session.state["result_start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Load summary data
        self._load_summary_data()

        st.subheader(msg.get("result_header"), divider=True)

        self._present_result_report()

        if st.button(msg.get("survey_complete_msg")):
            self.session.state["survey_completed"] = True
            st.rerun()

        return self.session.state.get("survey_completed") is True

    def _load_summary_data(self):
        """Load summary statistics from database."""
        try:
            db_handler = DatabaseHandler(db_read_allowed=self.db_read_allowed)
            summary = db_handler.load_table("Summary_Sessions")

            if not summary.empty:
                row = summary.iloc[0]
                self.session.state["sum_toxic_score"] = Decimal(str(row.get("sum_toxic_score", 0)))
                self.session.state["max_toxic_score"] = Decimal(str(row.get("max_toxic_score", 0)))
                self.session.state["min_toxic_score"] = Decimal(str(row.get("min_toxic_score", 0)))
                self.session.state["avg_toxic_score"] = Decimal(str(row.get("avg_toxic_score", 0)))
                self.session.state["sum_filter_violations"] = row.get("sum_filter_violations", 0)
                self.session.state["avg_filter_violations"] = row.get("avg_filter_violations", 0)
                self.session.state["count_guys"] = row.get("count_guys", 0)
        except Exception as e:
            st.warning(f"Could not load summary data: {e}")
            # Set defaults
            self.session.state["avg_toxic_score"] = Decimal("0.5")
            self.session.state["avg_filter_violations"] = 0

    def _present_result_report(self):
        """Present the result report to the user."""
        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        avg_toxic_score = self.session.state.get("avg_toxic_score", Decimal("0.5"))
        toxic_score = self.session.state.get("toxic_score", 0)
        avg_filter_violations = self.session.state.get("avg_filter_violations", 0)
        filter_violations = self.session.state.get("filter_violations", 0)
        bf_name = self.session.user_details.get("bf_name", "Your boyfriend")

        if toxic_score:
            st.info(msg.get("toxic_score_info", toxic_score=round(100 * toxic_score, 1)), icon="⚡")
            if Decimal(str(toxic_score)) > avg_toxic_score:
                st.error(msg.get("red_flag_fail_msg", bf_name=bf_name))
            else:
                st.success(msg.get("red_flag_pass_msg", bf_name=bf_name))
        else:
            st.success(msg.get("red_flag_pass_msg", bf_name=bf_name))

        st.divider()

        if filter_violations:
            if filter_violations > 0:
                st.error(msg.get("filter_fail_msg", bf_name=bf_name, filter_violations=filter_violations))
        else:
            st.success(msg.get("filter_pass_msg", bf_name=bf_name))

        st.divider()

        # Try to show toxic graph
        self._show_toxic_graph()

    def _show_toxic_graph(self):
        """Show toxicity comparison graph."""
        try:
            language = self.session.user_details.get("language") or "EN"
            msg = self.msg

            db_handler = DatabaseHandler(db_read_allowed=self.db_read_allowed)
            session_responses = db_handler.load_table("session_responses")

            if session_responses.empty:
                return

            toxic_score = self.session.state.get("toxic_score", 0)
            if toxic_score:
                # Simple visualization - could be enhanced with plotnine/matplotlib
                st.write(msg.get("toxic_graph_guy_cnt", guy_cnt=len(session_responses)))
        except Exception as e:
            # Silently fail if graph can't be shown
            pass

