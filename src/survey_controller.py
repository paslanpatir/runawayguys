import streamlit as st
from src.progress_manager import ProgressManager


class SurveyController:
    def __init__(self, steps):
        self.steps = steps
        self.progress_manager = ProgressManager(steps)
        if "current_step" not in st.session_state:
            st.session_state.current_step = 0

    def run(self):
        current_idx = st.session_state.current_step
        if current_idx < len(self.steps):
            step = self.steps[current_idx]

            # show progress
            self.progress_manager.show_progress(step.name)

            # run step
            done = step.run()
            if done:
                st.session_state.current_step += 1
                st.rerun()
