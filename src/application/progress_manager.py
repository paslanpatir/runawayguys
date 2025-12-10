"""Progress bar management for survey steps."""
import streamlit as st


class ProgressManager:
    """Manages and displays progress bar for survey steps."""

    def __init__(self, steps):
        # Store the ordered list of step names
        self.steps = [step.name for step in steps]
        self.total_steps = len(self.steps)

    def show_progress(self, current_step):
        """Render progress bar for current step."""
        try:
            idx = self.steps.index(current_step)
            progress = (idx + 1) / self.total_steps
        except ValueError:
            progress = 0.0
        
        # Display progress bar prominently
        st.progress(min(progress, 1.0))
        
        # Show progress text (step X of Y) - like the original counter-based approach
        try:
            idx = self.steps.index(current_step)
            st.caption(f"Step {idx + 1} of {self.total_steps}")
        except ValueError:
            pass

