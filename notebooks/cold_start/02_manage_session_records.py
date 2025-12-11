"""
Notebook: Manage Session Records in DynamoDB

This notebook provides utilities to manage session records:
- Delete a session record (by user_id and boyfriend_name) from all related tables
- Update a record in a selected table by session_id
- Automatically updates Summary_Sessions when records are deleted

Usage:
    # Delete a session
    delete_session(user_id="user123", boyfriend_name="John", db_write_allowed=True)
    
    # Update a record
    update_session_record(
        table_name="session_responses",
        session_id=123456789,
        update_data={"toxic_score": 0.75},
        db_write_allowed=True
    )
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.database.database_handler import DatabaseHandler
from src.utils.session_id_generator import generate_session_id, find_existing_session_id
from src.utils.summary_updater import update_summary_after_delete


def delete_session(user_id: str, boyfriend_name: str, db_write_allowed: bool = True) -> bool:
    """
    Delete a session record from all related tables based on user_id and boyfriend_name.
    Also updates Summary_Sessions table.
    
    Args:
        user_id: User ID of the record to delete
        boyfriend_name: Boyfriend name of the record to delete
        db_write_allowed: If True, use DynamoDB; if False, use CSV
        
    Returns:
        True if deletion was successful, False otherwise
    """
    print("=" * 60)
    print(f"Deleting Session Record")
    print("=" * 60)
    print(f"User ID: {user_id}")
    print(f"Boyfriend Name: {boyfriend_name}")
    print(f"Backend: {'DynamoDB' if db_write_allowed else 'CSV'}")
    print("=" * 60)
    
    db_handler = DatabaseHandler(db_write_allowed=db_write_allowed)
    
    try:
        # Find existing session_id
        session_id = find_existing_session_id(db_handler, "session_responses", user_id, boyfriend_name)
        
        if session_id is None:
            # Try generating it (in case record exists but wasn't found by search)
            session_id = generate_session_id(user_id, boyfriend_name)
            print(f"[INFO] Generated session_id {session_id}, checking if record exists...")
        
        # Load the record to get its values before deleting
        print(f"\n[1] Loading record with session_id {session_id} from session_responses...")
        session_responses = db_handler.load_table("session_responses")
        
        if session_responses.empty:
            print("[ERROR] session_responses table is empty")
            db_handler.close()
            return False
        
        # Find the record by session_id and verify user_id and boyfriend_name match
        record = session_responses[session_responses["id"] == session_id]
        
        if record.empty:
            print(f"[ERROR] Record with session_id={session_id} not found")
            db_handler.close()
            return False
        
        # Verify user_id and boyfriend_name match
        row = record.iloc[0]
        if str(row.get("user_id", "")).strip() != str(user_id).strip() or str(row.get("boyfriend_name", "")).strip() != str(boyfriend_name).strip():
            print(f"[ERROR] Record found but user_id or boyfriend_name doesn't match")
            print(f"     Expected: user_id={user_id}, boyfriend_name={boyfriend_name}")
            print(f"     Found: user_id={row.get('user_id')}, boyfriend_name={row.get('boyfriend_name')}")
            db_handler.close()
            return False
        
        # Get values for summary update
        deleted_toxic_score = float(row.get("toxic_score", 0))
        deleted_filter_violations = int(row.get("filter_violations", 0))
        
        print(f"[OK] Found record:")
        print(f"     Session ID: {session_id}")
        print(f"     Toxic Score: {deleted_toxic_score}")
        print(f"     Filter Violations: {deleted_filter_violations}")
        
        # Delete the record from all related tables
        print(f"\n[2] Deleting records with session_id {session_id} from all tables...")
        tables_to_delete = [
            "session_responses",
            "session_gtk_responses",
            "session_feedback",
            "session_toxicity_rating",
            "session_insights",
        ]
        
        deleted_count = 0
        for table_name in tables_to_delete:
            try:
                if db_handler.delete_record(table_name, session_id, id_column="id"):
                    deleted_count += 1
                    print(f"[OK] Deleted from {table_name}")
                else:
                    print(f"[INFO] No record found in {table_name} (may not exist for this session)")
            except Exception as e:
                print(f"[WARNING] Could not delete from {table_name}: {e}")
        
        if deleted_count == 0:
            print("[ERROR] Failed to delete any records")
            db_handler.close()
            return False
        
        # Update Summary_Sessions
        print(f"\n[3] Updating Summary_Sessions...")
        update_success = update_summary_after_delete(
            db_handler=db_handler,
            deleted_toxic_score=deleted_toxic_score,
            deleted_filter_violations=deleted_filter_violations,
        )
        
        if not update_success:
            print("[WARNING] Record deleted but Summary_Sessions update failed")
        
        db_handler.close()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Session record deleted and Summary_Sessions updated!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error deleting session: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        db_handler.close()
        return False


def update_session_record(
    table_name: str,
    session_id: int,
    update_data: Dict[str, Any],
    db_write_allowed: bool = True
) -> bool:
    """
    Update a record in a specific table by session_id.
    
    Args:
        table_name: Name of the table to update
        session_id: Session ID of the record to update
        update_data: Dictionary of fields to update
        db_write_allowed: If True, use DynamoDB; if False, use CSV
        
    Returns:
        True if update was successful, False otherwise
    """
    print("=" * 60)
    print(f"Updating Session Record")
    print("=" * 60)
    print(f"Table: {table_name}")
    print(f"Session ID: {session_id}")
    print(f"Backend: {'DynamoDB' if db_write_allowed else 'CSV'}")
    print("=" * 60)
    
    db_handler = DatabaseHandler(db_write_allowed=db_write_allowed)
    
    try:
        # Check if record exists
        print(f"\n[1] Checking if record exists in {table_name}...")
        table_data = db_handler.load_table(table_name)
        
        if table_data.empty:
            print(f"[ERROR] Table '{table_name}' is empty")
            db_handler.close()
            return False
        
        # Find the record
        record = table_data[table_data["id"] == session_id]
        
        if record.empty:
            print(f"[ERROR] Record with session_id={session_id} not found in {table_name}")
            db_handler.close()
            return False
        
        print(f"[OK] Found record in {table_name}")
        print(f"     Current values: {dict(record.iloc[0].head(5))}...")
        
        # Update the record
        print(f"\n[2] Updating record...")
        print(f"     Fields to update: {list(update_data.keys())}")
        
        db_handler.update_record(
            table_name=table_name,
            key_dict={"id": session_id},
            update_dict=update_data
        )
        
        print(f"[OK] Record updated successfully!")
        
        db_handler.close()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Record updated!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error updating record: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        db_handler.close()
        return False


def list_sessions(user_id: Optional[str] = None, db_write_allowed: bool = True) -> None:
    """
    List all sessions or sessions for a specific user.
    
    Args:
        user_id: Optional user ID to filter by. If None, lists all sessions.
        db_write_allowed: If True, use DynamoDB; if False, use CSV
    """
    print("=" * 60)
    print("Listing Sessions")
    print("=" * 60)
    if user_id:
        print(f"Filter: user_id = {user_id}")
    else:
        print("Filter: All sessions")
    print("=" * 60)
    
    db_handler = DatabaseHandler(db_write_allowed=db_write_allowed)
    
    try:
        session_responses = db_handler.load_table("session_responses")
        
        if session_responses.empty:
            print("[INFO] No sessions found")
            db_handler.close()
            return
        
        # Filter by user_id if provided
        if user_id:
            filtered = session_responses[session_responses["user_id"] == user_id]
        else:
            filtered = session_responses
        
        if filtered.empty:
            print(f"[INFO] No sessions found for user_id={user_id}")
            db_handler.close()
            return
        
        print(f"\n[OK] Found {len(filtered)} session(s):\n")
        
        # Display sessions
        for idx, (_, row) in enumerate(filtered.iterrows(), 1):
            print(f"Session {idx}:")
            print(f"  Session ID: {row.get('id')}")
            print(f"  User ID: {row.get('user_id')}")
            print(f"  Name: {row.get('name')}")
            print(f"  Boyfriend Name: {row.get('boyfriend_name')}")
            print(f"  Toxic Score: {row.get('toxic_score')}")
            print(f"  Filter Violations: {row.get('filter_violations')}")
            print(f"  Language: {row.get('language')}")
            print(f"  Session Start: {row.get('session_start_time')}")
            print()
        
        db_handler.close()
        
    except Exception as e:
        print(f"\n[ERROR] Error listing sessions: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        db_handler.close()


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage session records in DynamoDB/CSV")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a session record')
    delete_parser.add_argument('user_id', help='User ID')
    delete_parser.add_argument('boyfriend_name', help='Boyfriend name')
    delete_parser.add_argument('--csv', action='store_true', help='Use CSV instead of DynamoDB')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a session record')
    update_parser.add_argument('table_name', help='Table name')
    update_parser.add_argument('session_id', type=int, help='Session ID')
    update_parser.add_argument('--field', action='append', nargs=2, metavar=('KEY', 'VALUE'),
                              help='Field to update (can be used multiple times)')
    update_parser.add_argument('--csv', action='store_true', help='Use CSV instead of DynamoDB')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List sessions')
    list_parser.add_argument('--user-id', help='Filter by user ID')
    list_parser.add_argument('--csv', action='store_true', help='Use CSV instead of DynamoDB')
    
    args = parser.parse_args()
    
    if args.command == 'delete':
        success = delete_session(args.user_id, args.boyfriend_name, db_write_allowed=not args.csv)
        sys.exit(0 if success else 1)
    elif args.command == 'update':
        if not args.field:
            print("[ERROR] At least one --field KEY VALUE must be provided")
            sys.exit(1)
        update_data = {k: v for k, v in args.field}
        success = update_session_record(args.table_name, args.session_id, update_data, db_write_allowed=not args.csv)
        sys.exit(0 if success else 1)
    elif args.command == 'list':
        list_sessions(user_id=args.user_id, db_write_allowed=not args.csv)
    else:
        parser.print_help()
        sys.exit(1)

