"""Database handler factory that selects the appropriate adapter."""
from src.ports.database_port import DatabasePort
from src.adapters.database.dynamodb_adapter import DynamoDBAdapter
from src.adapters.database.csv_adapter import CSVAdapter


class DatabaseHandler:
    """Factory that creates the appropriate database adapter based on configuration."""

    def __init__(self, db_read_allowed: bool = False, db_write_allowed: bool = False):
        """
        Initialize database handler.
        
        Args:
            db_read_allowed: If True, use DynamoDB for reads
            db_write_allowed: If True, use DynamoDB for writes
        """
        if db_read_allowed or db_write_allowed:
            self.backend: DatabasePort = DynamoDBAdapter()
        else:
            self.backend: DatabasePort = CSVAdapter()

    def load_table(self, table_name: str):
        """Load data from a table."""
        return self.backend.load_table(table_name)

    def add_record(self, table_name: str, newdata_dict: dict):
        """Add a new record to a table."""
        return self.backend.add_record(table_name, newdata_dict)

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict):
        """Update an existing record in a table."""
        return self.backend.update_record(table_name, key_dict, update_dict)

    def close(self):
        """Close the database connection."""
        self.backend.close()

