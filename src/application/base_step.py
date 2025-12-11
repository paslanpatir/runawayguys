"""Base class for all survey steps."""
from src.application.session_manager import SessionManager
from src.application.messages import Message


class BaseStep:
    """Base class for all app steps with session + messaging helpers."""

    def __init__(self):
        # Initialize session state wrapper
        self.session = SessionManager()
        # Message object will be created dynamically in msg property
        self._msg = None

    @property
    def msg(self):
        """Access the Message object, creating it with current language if needed."""
        if self._msg is None:
            # Use "Neutral" (capital N) to match Message class default
            lang = self.session.user_details.get("language") or "Neutral"
            self._msg = Message(lang)
        else:
            # Update language if it has changed
            current_lang = self.session.user_details.get("language") or "Neutral"
            if self._msg.language != current_lang:
                self._msg = Message(current_lang)
        return self._msg

    def run(self):
        """Every step must implement this."""
        raise NotImplementedError("Each step must implement the run() method")

