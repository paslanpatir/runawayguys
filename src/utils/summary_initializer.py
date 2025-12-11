"""Utility functions for initializing Summary_Sessions table with default values."""
from decimal import Decimal
from datetime import datetime
from src.adapters.database.database_handler import DatabaseHandler
from src.utils.constants import DATE_FORMAT


def initialize_summary_sessions(db_handler: DatabaseHandler) -> bool:
    """
    Initialize Summary_Sessions table with default values if it's empty.
    
    Args:
        db_handler: DatabaseHandler instance
        
    Returns:
        True if initialization was successful, False otherwise
    """
    try:
        # Check if Summary_Sessions exists and has data
        summary = db_handler.load_table("Summary_Sessions")
        
        if not summary.empty:
            print("[INFO] Summary_Sessions already has data, skipping initialization")
            return True
        
        # Create default record
        default_record = {
            "summary_id": 1,
            "sum_toxic_score": Decimal("0"),
            "max_toxic_score": Decimal("1"),  # Start at 1 (max possible is 1.0) - will be updated when real data comes
            "min_toxic_score": Decimal("0"),  # Start at 0 (min possible is 0.0) - will be updated when real data comes
            "avg_toxic_score": Decimal("0.5"),  # Default average
            "sum_filter_violations": 0,
            "avg_filter_violations": Decimal("0"),
            "count_guys": 0,
            "max_id_session_responses": 0,
            "max_id_gtk_responses": 0,
            "max_id_feedback": 0,
            "max_id_session_toxicity_rating": 0,
            "last_update_date": datetime.now().strftime(DATE_FORMAT),
        }
        
        # Add the default record
        db_handler.add_record("Summary_Sessions", default_record)
        print("[OK] Initialized Summary_Sessions with default values")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize Summary_Sessions: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

