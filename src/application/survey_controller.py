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

            # Show current step in terminal
            step_names = [
                "Language Selection", "User Details", "Boyfriend Name", "Welcome & GTK Questions",
                "Filter Questions", "RedFlag Questions", 
                "Toxicity Opinion", "Results", "Feedback", "Report"
            ]
            step_name = step_names[current_idx] if current_idx < len(step_names) else step.name
            print(f"[STEP {current_idx + 1}/{len(self.steps)}] {step_name}")

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
            print("[COMPLETED] All survey steps completed")

