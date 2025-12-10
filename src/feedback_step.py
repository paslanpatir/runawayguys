"""Feedback step."""
import streamlit as st
from src.base_step import BaseStep


class FeedbackStep(BaseStep):
    name = "feedback"

    def run(self):
        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("enter_feedback_msg"), divider=True)

        sentiment_mapping = msg.get("sentiment_mapping")
        selected = st.feedback("stars")

        if selected is None:
            st.warning(msg.get("please_rate_msg"))
            rating = None
        else:
            # Convert feedback to 1-based index
            rating = selected + 1
            st.markdown(msg.get("feedback_result_msg", star=sentiment_mapping[rating - 1]))

        if st.button(msg.get("continue_msg")):
            if rating:
                self.session.state["feedback_rating"] = rating
                st.rerun()
            else:
                st.error(msg.get("please_rate_msg"))

        return self.session.state.get("feedback_rating") is not None

