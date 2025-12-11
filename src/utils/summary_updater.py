"""Utility functions for updating Summary_Sessions table when records are deleted."""
from decimal import Decimal
from typing import Optional
from src.adapters.database.database_handler import DatabaseHandler


def update_summary_after_delete(
    db_handler: DatabaseHandler,
    deleted_toxic_score: Optional[float] = None,
    deleted_filter_violations: Optional[int] = None,
) -> bool:
    """
    Update Summary_Sessions table after a record is deleted.
    
    Args:
        db_handler: DatabaseHandler instance
        deleted_toxic_score: Toxic score of the deleted record (optional, will be recalculated if None)
        deleted_filter_violations: Filter violations of the deleted record (optional, will be recalculated if None)
        
    Returns:
        True if update was successful, False otherwise
    """
    try:
        # Load current summary
        summary = db_handler.load_table("Summary_Sessions")
        
        if summary.empty:
            print("[WARNING] Summary_Sessions is empty, cannot update after delete")
            return False
        
        row = summary.iloc[0]
        
        # Get current values
        sum_toxic_score = Decimal(str(row.get("sum_toxic_score", 0)))
        count_guys = int(row.get("count_guys", 0))
        sum_filter_violations = int(row.get("sum_filter_violations", 0))
        max_toxic_score = Decimal(str(row.get("max_toxic_score", 1)))
        min_toxic_score = Decimal(str(row.get("min_toxic_score", 0)))
        
        # If deleted values not provided, recalculate from remaining records
        if deleted_toxic_score is None or deleted_filter_violations is None:
            # Recalculate from all remaining session_responses
            try:
                session_responses = db_handler.load_table("session_responses")
                if not session_responses.empty:
                    if deleted_toxic_score is None:
                        # Recalculate sum and averages from remaining records
                        if "toxic_score" in session_responses.columns:
                            sum_toxic_score = Decimal(str(session_responses["toxic_score"].sum()))
                            count_guys = len(session_responses)
                            if count_guys > 0:
                                avg_toxic_score = sum_toxic_score / Decimal(str(count_guys))
                                max_toxic_score = Decimal(str(session_responses["toxic_score"].max()))
                                min_toxic_score = Decimal(str(session_responses["toxic_score"].min()))
                            else:
                                avg_toxic_score = Decimal("0")
                                max_toxic_score = Decimal("0")
                                min_toxic_score = Decimal("0")
                        else:
                            # No toxic_score column, set to defaults
                            sum_toxic_score = Decimal("0")
                            count_guys = len(session_responses)
                            avg_toxic_score = Decimal("0")
                            max_toxic_score = Decimal("0")
                            min_toxic_score = Decimal("0")
                    else:
                        # Use provided deleted_toxic_score
                        sum_toxic_score = sum_toxic_score - Decimal(str(deleted_toxic_score))
                        count_guys = max(0, count_guys - 1)
                        if count_guys > 0:
                            avg_toxic_score = sum_toxic_score / Decimal(str(count_guys))
                            # Recalculate max/min from remaining records
                            if "toxic_score" in session_responses.columns:
                                max_toxic_score = Decimal(str(session_responses["toxic_score"].max()))
                                min_toxic_score = Decimal(str(session_responses["toxic_score"].min()))
                        else:
                            avg_toxic_score = Decimal("0")
                            max_toxic_score = Decimal("0")
                            min_toxic_score = Decimal("0")
                    
                    if deleted_filter_violations is None:
                        # Recalculate filter violations from remaining records
                        if "filter_violations" in session_responses.columns:
                            sum_filter_violations = int(session_responses["filter_violations"].sum())
                        else:
                            sum_filter_violations = 0
                    else:
                        # Use provided deleted_filter_violations
                        sum_filter_violations = max(0, sum_filter_violations - deleted_filter_violations)
                else:
                    # No remaining records
                    count_guys = 0
                    sum_toxic_score = Decimal("0")
                    avg_toxic_score = Decimal("0")
                    max_toxic_score = Decimal("0")
                    min_toxic_score = Decimal("0")
                    sum_filter_violations = 0
            except Exception as e:
                print(f"[WARNING] Could not recalculate from remaining records: {e}")
                # Fallback: subtract provided values or set to defaults
                if deleted_toxic_score is not None:
                    sum_toxic_score = max(Decimal("0"), sum_toxic_score - Decimal(str(deleted_toxic_score)))
                count_guys = max(0, count_guys - 1)
                if count_guys > 0:
                    avg_toxic_score = sum_toxic_score / Decimal(str(count_guys))
                else:
                    avg_toxic_score = Decimal("0")
                    max_toxic_score = Decimal("0")
                    min_toxic_score = Decimal("0")
                
                if deleted_filter_violations is not None:
                    sum_filter_violations = max(0, sum_filter_violations - deleted_filter_violations)
        else:
            # Use provided deleted values
            sum_toxic_score = max(Decimal("0"), sum_toxic_score - Decimal(str(deleted_toxic_score)))
            count_guys = max(0, count_guys - 1)
            sum_filter_violations = max(0, sum_filter_violations - deleted_filter_violations)
            
            if count_guys > 0:
                avg_toxic_score = sum_toxic_score / Decimal(str(count_guys))
                avg_filter_violations = Decimal(str(sum_filter_violations)) / Decimal(str(count_guys))
                
                # Recalculate max/min from remaining records
                try:
                    session_responses = db_handler.load_table("session_responses")
                    if not session_responses.empty and "toxic_score" in session_responses.columns:
                        max_toxic_score = Decimal(str(session_responses["toxic_score"].max()))
                        min_toxic_score = Decimal(str(session_responses["toxic_score"].min()))
                except:
                    pass  # Keep existing max/min if recalculation fails
            else:
                avg_toxic_score = Decimal("0")
                avg_filter_violations = Decimal("0")
                max_toxic_score = Decimal("0")
                min_toxic_score = Decimal("0")
        
        # Calculate avg_filter_violations
        if count_guys > 0:
            avg_filter_violations = Decimal(str(sum_filter_violations)) / Decimal(str(count_guys))
        else:
            avg_filter_violations = Decimal("0")
        
        # Note: max_id tracking removed - IDs are now hash-based and order-agnostic
        # We no longer need to track max IDs since session_ids are generated deterministically
        # from user_id + boyfriend_name, not sequentially
        
        # Prepare update dictionary
        # DynamoDB requires Decimal types for numeric values, not float
        # CSV adapter will handle Decimal conversion automatically
        from datetime import datetime
        from src.utils.constants import DATE_FORMAT
        update_dict = {
            "sum_toxic_score": sum_toxic_score,  # Keep as Decimal for DynamoDB
            "max_toxic_score": max_toxic_score,  # Keep as Decimal for DynamoDB
            "min_toxic_score": min_toxic_score,  # Keep as Decimal for DynamoDB
            "avg_toxic_score": avg_toxic_score,  # Keep as Decimal for DynamoDB
            "sum_filter_violations": sum_filter_violations,  # int is fine
            "avg_filter_violations": avg_filter_violations,  # Keep as Decimal for DynamoDB
            "count_guys": count_guys,  # int is fine
            # max_id fields kept for backward compatibility but set to 0 (no longer tracked)
            "max_id_session_responses": 0,
            "max_id_gtk_responses": 0,
            "max_id_feedback": 0,
            "max_id_session_toxicity_rating": 0,
            "last_update_date": datetime.now().strftime(DATE_FORMAT),
        }
        
        # Update Summary_Sessions
        db_handler.update_record("Summary_Sessions", {"summary_id": 1}, update_dict)
        print(f"[OK] Updated Summary_Sessions after delete. New count_guys: {count_guys}, avg_toxic_score: {float(avg_toxic_score):.4f}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update Summary_Sessions after delete: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

