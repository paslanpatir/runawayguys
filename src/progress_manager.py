import streamlit as st

class ProgressManager:
    def __init__(self, steps):
        # Store the ordered list of step names
        self.steps = [step.name for step in steps]

    def show_progress(self, current_step):
        """Render progress bar for current step."""
        try:
            idx = self.steps.index(current_step)
            progress = (idx + 1) / len(self.steps)
        except ValueError:
            progress = 0.0
        st.progress(min(progress, 1.0))
