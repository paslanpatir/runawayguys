from src.messages import Message
from src.session_manager import SessionManager


class BaseStep:
    """Base class for all survey steps."""
    name = "base"

    def __init__(self):
        self.session = SessionManager()

    def run(self):
        raise NotImplementedError("Each step must implement run()")

    @property
    def language(self):
        return self.session.language

    @property
    def msg(self):
        return Message(self.language)
