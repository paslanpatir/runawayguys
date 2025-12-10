"""Value objects for survey data structures."""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import pandas as pd


@dataclass
class UserDetails:
    """User information value object."""
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    language: Optional[str] = None
    bf_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "language": self.language,
            "bf_name": self.bf_name,
        }


@dataclass
class FilterQuestion:
    """Filter question value object (read from RedFlagFilters table)."""
    filter_id: int
    filter_name: str
    scoring: str  # "Limit" or "YES/NO"
    upper_limit: int
    question_tr: str
    question_en: str

    def get_question(self, language: str) -> str:
        """Get question text based on language."""
        if language == "TR":
            return self.question_tr
        return self.question_en

    @classmethod
    def from_dataframe_row(cls, row) -> "FilterQuestion":
        """Create from pandas DataFrame row."""
        return cls(
            filter_id=int(row["Filter_ID"]),
            filter_name=str(row.get("Filter_Name", "")),
            scoring=str(row["Scoring"]),
            upper_limit=int(row["Upper_Limit"]),
            question_tr=str(row["Filter_Question_TR"]),
            question_en=str(row["Filter_Question_EN"]),
        )


@dataclass
class RedFlagQuestion:
    """RedFlag question value object (read from RedFlagQuestions table)."""
    question_id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    redflag_id: Optional[int] = None
    redflag_name: Optional[str] = None
    scoring: str = "Range(0-10)"  # "Range(0-10)" or "YES/NO"
    weight: float = 1.0
    worst_situation: Optional[str] = None
    question_tr: str = ""
    question_en: str = ""
    hint: Optional[str] = None

    def get_question(self, language: str) -> str:
        """Get question text based on language."""
        if language == "TR":
            return self.question_tr
        return self.question_en

    @classmethod
    def from_dataframe_row(cls, row) -> "RedFlagQuestion":
        """Create from pandas DataFrame row."""
        return cls(
            question_id=int(row["ID"]),
            category_id=int(row["Category_ID"]) if pd.notna(row.get("Category_ID")) else None,
            category_name=str(row.get("Category_Name", "")) if pd.notna(row.get("Category_Name")) else None,
            redflag_id=int(row["RedFLag_ID"]) if pd.notna(row.get("RedFLag_ID")) else None,
            redflag_name=str(row.get("RedFlag_Name", "")) if pd.notna(row.get("RedFlag_Name")) else None,
            scoring=str(row["Scoring"]),
            weight=float(row["Weight"]) if pd.notna(row.get("Weight")) else 1.0,
            worst_situation=str(row.get("Worst_Situation", "")) if pd.notna(row.get("Worst_Situation")) else None,
            question_tr=str(row["Question_TR"]),
            question_en=str(row["Question_EN"]),
            hint=str(row.get("Hint", "")) if pd.notna(row.get("Hint")) else None,
        )


@dataclass
class GTKQuestion:
    """GetToKnow question value object (read from GetToKnowQuestions table)."""
    gtk_id: int
    gtk_name: Optional[str] = None
    scoring: str = "Range(0-10)"
    levels_tr: Optional[list] = None
    levels_en: Optional[list] = None
    question_tr: str = ""
    question_en: str = ""
    hint: Optional[str] = None

    def get_question(self, language: str) -> str:
        """Get question text based on language."""
        if language == "TR":
            return self.question_tr
        return self.question_en

    def get_levels(self, language: str) -> Optional[list]:
        """Get levels based on language."""
        if language == "TR":
            return self.levels_tr
        return self.levels_en

    @classmethod
    def from_dataframe_row(cls, row) -> "GTKQuestion":
        """Create from pandas DataFrame row."""
        import ast
        import pandas as pd

        levels_tr = None
        levels_en = None

        if pd.notna(row.get("Levels_TR")):
            try:
                levels_tr = ast.literal_eval(str(row["Levels_TR"]))
            except (ValueError, SyntaxError):
                pass

        if pd.notna(row.get("Levels_EN")):
            try:
                levels_en = ast.literal_eval(str(row["Levels_EN"]))
            except (ValueError, SyntaxError):
                pass

        return cls(
            gtk_id=int(row["GTK_ID"]),
            gtk_name=str(row.get("GTK_Name", "")) if pd.notna(row.get("GTK_Name")) else None,
            scoring=str(row["Scoring"]),
            levels_tr=levels_tr,
            levels_en=levels_en,
            question_tr=str(row["Question_TR"]),
            question_en=str(row["Question_EN"]),
            hint=str(row.get("Hint", "")) if pd.notna(row.get("Hint")) else None,
        )


@dataclass
class FilterResponse:
    """Filter question responses value object."""
    responses: Dict[str, int]  # e.g., {"F1": 0, "F2": 1, ...}
    violations: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "filter_responses": self.responses,
            "filter_violations": self.violations,
        }


@dataclass
class RedFlagResponse:
    """RedFlag question responses value object."""
    responses: Dict[str, Any]  # e.g., {"Q1": 5, "Q2": 7, ...} (can include NaN)
    toxic_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "redflag_responses": self.responses,
            "toxic_score": self.toxic_score,
        }


@dataclass
class GTKResponse:
    """GetToKnow question responses value object."""
    responses: Dict[str, int]  # e.g., {"GTK1": 1, "GTK2": 2, ...}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return self.responses


@dataclass
class SessionResponse:
    """Session response value object (for session_responses table)."""
    id: Optional[int] = None
    user_id: str = ""
    name: Optional[str] = None
    email: Optional[str] = None
    boyfriend_name: Optional[str] = None
    language: Optional[str] = None
    toxic_score: Optional[Decimal] = None
    filter_violations: Optional[Decimal] = None
    session_start_time: Optional[str] = None
    result_start_time: Optional[str] = None
    session_end_time: Optional[str] = None
    redflag_responses: Dict[str, Decimal] = field(default_factory=dict)
    filter_responses: Dict[str, Decimal] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "boyfriend_name": self.boyfriend_name,
            "language": self.language,
            "toxic_score": self.toxic_score,
            "filter_violations": self.filter_violations,
            "session_start_time": self.session_start_time,
            "result_start_time": self.result_start_time,
            "session_end_time": self.session_end_time,
        }
        # Add redflag and filter responses
        result.update({k: v for k, v in self.redflag_responses.items()})
        result.update({k: v for k, v in self.filter_responses.items()})
        return result


@dataclass
class GTKResponseRecord:
    """GTK response record value object (for session_gtk_responses table)."""
    id: Optional[int] = None
    user_id: str = ""
    name: Optional[str] = None
    email: Optional[str] = None
    boyfriend_name: Optional[str] = None
    language: Optional[str] = None
    test_date: Optional[str] = None
    gtk_responses: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "boyfriend_name": self.boyfriend_name,
            "language": self.language,
            "test_date": self.test_date,
        }
        result.update(self.gtk_responses)
        return result


@dataclass
class ToxicityRatingRecord:
    """Toxicity rating record value object (for session_toxicity_rating table)."""
    id: Optional[int] = None
    user_id: str = ""
    name: Optional[str] = None
    email: Optional[str] = None
    boyfriend_name: Optional[str] = None
    language: Optional[str] = None
    test_date: Optional[str] = None
    toxicity_rating: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "boyfriend_name": self.boyfriend_name,
            "language": self.language,
            "test_date": self.test_date,
            "toxicity_rating": self.toxicity_rating,
        }


@dataclass
class FeedbackRecord:
    """Feedback record value object (for session_feedback table)."""
    id: Optional[int] = None
    user_id: str = ""
    user_name: Optional[str] = None
    email: Optional[str] = None
    boyfriend_name: Optional[str] = None
    language: Optional[str] = None
    test_date: Optional[str] = None
    rating: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "email": self.email,
            "boyfriend_name": self.boyfriend_name,
            "language": self.language,
            "test_date": self.test_date,
            "rating": self.rating,
        }

