"""Port (interface) for email operations."""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict


class EmailPort(ABC):
    """Abstract interface for email operations."""

    @abstractmethod
    def send_report(
        self,
        recipient_email: str,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        language: str = "EN",
        insights: str = None,
        category_scores: Optional[Dict[str, Tuple[float, int]]] = None,
    ) -> bool:
        """
        Send a survey report email.
        
        Args:
            recipient_email: Email address to send to
            user_name: Name of the user
            bf_name: Boyfriend's name
            toxic_score: Toxicity score (0-1)
            avg_toxic_score: Average toxicity score from all users (0-1)
            filter_violations: Number of filter violations
            violated_filter_questions: List of violated filter questions (question_text, answer, filter_id)
            language: Language code (TR or EN)
            insights: AI-generated insights (optional)
            category_scores: Dictionary mapping category_name to (average_score, question_count) (optional)
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the email connection."""
        pass

