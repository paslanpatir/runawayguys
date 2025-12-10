"""Toxicity opinion step."""
import streamlit as st
from src.application.base_step import BaseStep


class ToxicityOpinionStep(BaseStep):
    name = "toxicity_opinion"

    def run(self):
        language = self.session.user_details.get("language") or "EN"
        msg = self.msg

        st.subheader(msg.get("toxicity_self_rating"), divider=True)

        opt = msg.get("toxicity_answer")
        selected = st.select_slider(
            msg.get("select_toxicity_msg"),
            options=opt,
            label_visibility="hidden",
            value=opt[2] if len(opt) > 2 else opt[0]
        )

        # Map the selected option to an integer value (1 to 5)
        toxicity_rating = opt.index(selected) + 1
        st.markdown(msg.get("rating_result_msg", selected=selected))
        st.markdown(msg.get("toxicity_result_msg", toxicity_rating=toxicity_rating))

        if st.button(msg.get("see_results")):
            self.session.state["toxicity_rating"] = toxicity_rating
            st.rerun()

        return self.session.state.get("toxicity_rating") is not None

