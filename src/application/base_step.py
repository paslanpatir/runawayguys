"""Base class for all survey steps."""
from src.application.session_manager import SessionManager
from src.application.messages import Message


class BaseStep:
    """Base class for all app steps with session + messaging helpers."""

    def __init__(self):
        # Initialize session state wrapper
        self.session = SessionManager()

        # Store Message object directly
        lang = self.session.user_details.get("language") or "NEUTRAL"
        self._msg = Message(lang)  # private variable

    @property
    def msg(self):
        """Access the Message object."""
        return self._msg

    def run(self):
        """Every step must implement this."""
        raise NotImplementedError("Each step must implement the run() method")

