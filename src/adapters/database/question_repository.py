"""Repository for loading questions as value objects."""
from typing import List
import pandas as pd
from src.adapters.database.database_handler import DatabaseHandler
from src.domain.value_objects import FilterQuestion, RedFlagQuestion, GTKQuestion
from src.domain.mappers import map_filter_questions, map_redflag_questions, map_gtk_questions


class QuestionRepository:
    """Repository for loading questions from database."""

    def __init__(self, db_handler: DatabaseHandler):
        self.db_handler = db_handler

    def get_filter_questions(self) -> List[FilterQuestion]:
        """Load filter questions as value objects."""
        df = self.db_handler.load_table("RedFlagFilters")
        return map_filter_questions(df)

    def get_redflag_questions(self) -> List[RedFlagQuestion]:
        """Load redflag questions as value objects."""
        df = self.db_handler.load_table("RedFlagQuestions")
        return map_redflag_questions(df)

    def get_gtk_questions(self) -> List[GTKQuestion]:
        """Load GTK questions as value objects."""
        df = self.db_handler.load_table("GetToKnowQuestions")
        return map_gtk_questions(df)

