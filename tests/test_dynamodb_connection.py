"""Test script to check DynamoDB connection."""
import sys
from src.infrastructure.connection_manager import ConnectionManager
from src.adapters.database.database_handler import DatabaseHandler


def test_dynamodb_connection():
    """Test DynamoDB connection and list available tables."""
    print("=" * 60)
    print("Testing DynamoDB Connection")
    print("=" * 60)
    
    try:
        # Test connection manager
        print("\n[1] Testing ConnectionManager...")
        conn_manager = ConnectionManager()
        dynamodb = conn_manager.connect()
        print("[OK] DynamoDB connection established")
        
        # List tables
        print("\n[2] Listing DynamoDB tables...")
        table_list = list(dynamodb.tables.all())
        if table_list:
            print(f"[OK] Found {len(table_list)} table(s):")
            for table in table_list:
                print(f"  - {table.name}")
        else:
            print("[INFO] No tables found in DynamoDB")
        
        # Test DatabaseHandler with DB_READ=True
        print("\n[3] Testing DatabaseHandler (DynamoDB mode)...")
        db_handler = DatabaseHandler(db_read_allowed=True)
        
        # Try to load a common table
        test_tables = ["RedFlagQuestions", "RedFlagFilters", "Summary_Sessions"]
        for table_name in test_tables:
            try:
                print(f"\n[4] Testing load_table('{table_name}')...")
                df = db_handler.load_table(table_name)
                if not df.empty:
                    print(f"[OK] Table '{table_name}' loaded successfully")
                    print(f"     Rows: {len(df)}, Columns: {list(df.columns)[:5]}...")
                else:
                    print(f"[INFO] Table '{table_name}' exists but is empty")
            except Exception as e:
                print(f"[WARNING] Could not load table '{table_name}': {e}")
        
        db_handler.close()
        conn_manager.close()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] DynamoDB connection test completed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"[ERROR] DynamoDB connection test failed: {e}")
        print("=" * 60)
        import traceback
        print("\nTraceback:")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = test_dynamodb_connection()
    sys.exit(0 if success else 1)

