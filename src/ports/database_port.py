"""Port (interface) for database operations."""
from abc import ABC, abstractmethod
import pandas as pd


class DatabasePort(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load data from a table."""
        pass

    @abstractmethod
    def add_record(self, table_name: str, newdata_dict: dict) -> bool:
        """Add a new record to a table."""
        pass

    @abstractmethod
    def update_record(self, table_name: str, key_dict: dict, update_dict: dict) -> None:
        """Update an existing record in a table."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

