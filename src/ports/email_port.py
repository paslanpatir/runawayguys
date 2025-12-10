"""Port (interface) for email operations."""
from abc import ABC, abstractmethod


class EmailPort(ABC):
    """Abstract interface for email operations."""

    @abstractmethod
    def send_report(
        self,
        recipient_email: str,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        filter_violations: int,
        language: str = "EN",
        insights: str = None,
    ) -> bool:
        """Send a survey report email."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the email connection."""
        pass

