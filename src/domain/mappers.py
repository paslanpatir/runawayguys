"""Mappers to convert between DataFrames and value objects."""
import pandas as pd
from typing import List
from src.domain.value_objects import FilterQuestion, RedFlagQuestion, GTKQuestion


def map_filter_questions(df: pd.DataFrame) -> List[FilterQuestion]:
    """Convert DataFrame to list of FilterQuestion value objects."""
    if df.empty:
        return []
    return [FilterQuestion.from_dataframe_row(row) for _, row in df.iterrows()]


def map_redflag_questions(df: pd.DataFrame) -> List[RedFlagQuestion]:
    """Convert DataFrame to list of RedFlagQuestion value objects."""
    if df.empty:
        return []
    return [RedFlagQuestion.from_dataframe_row(row) for _, row in df.iterrows()]


def map_gtk_questions(df: pd.DataFrame) -> List[GTKQuestion]:
    """Convert DataFrame to list of GTKQuestion value objects."""
    if df.empty:
        return []
    return [GTKQuestion.from_dataframe_row(row) for _, row in df.iterrows()]

