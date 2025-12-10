"""Survey flow controller."""
import streamlit as st
from src.application.progress_manager import ProgressManager


class SurveyController:
    """Controls the flow of survey steps."""

    def __init__(self, steps):
        self.steps = steps
        self.progress_manager = ProgressManager(steps)
        if "current_step" not in st.session_state:
            st.session_state.current_step = 0

    def run(self):
        """Run the current step and advance if completed."""
        current_idx = st.session_state.current_step
        if current_idx < len(self.steps):
            step = self.steps[current_idx]

            # show progress bar at the top
            self.progress_manager.show_progress(step.name)

            # run step
            done = step.run()
            if done:
                st.session_state.current_step += 1
                st.rerun()
        else:
            # All steps completed, show 100% progress
            st.progress(1.0)

