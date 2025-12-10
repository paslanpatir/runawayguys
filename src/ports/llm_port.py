"""Port (interface) for LLM operations."""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple


class LLMPort(ABC):
    """Abstract interface for LLM operations."""

    @abstractmethod
    def generate_insights(
        self,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        language: str = "EN",
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
    ) -> Optional[str]:
        """
        Generate insights based on survey results.
        
        Args:
            user_name: Name of the user
            bf_name: Boyfriend's name
            toxic_score: Toxicity score (0-1)
            avg_toxic_score: Average toxicity score from all users (0-1)
            filter_violations: Number of filter violations
            violated_filter_questions: List of tuples (question_text, answer, filter_id) for violated filters
            language: Language code (TR or EN)
            top_redflag_questions: List of tuples (question_text, rating, question_id) for top-rated questions
            
        Returns:
            Generated insights text or None if generation fails
        """
        pass

