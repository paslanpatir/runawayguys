# Cold Start Notebooks

This folder contains notebooks for initializing and managing DynamoDB tables.

## Notebooks

### 1. `01_initialize_dynamodb_tables.py`

Initializes all DynamoDB output tables needed for the Runaway Guys application.

**Tables initialized:**
- `session_responses` - Main survey responses
- `session_gtk_responses` - Get-to-know questions responses
- `session_feedback` - User feedback ratings
- `session_toxicity_rating` - Toxicity opinion ratings
- `session_insights` - AI-generated insights metadata
- `Summary_Sessions` - Aggregated statistics across all sessions

**Usage:**
```bash
python notebooks/cold_start/01_initialize_dynamodb_tables.py
```

**Features:**
- Checks if tables already exist (won't recreate existing tables)
- Creates tables with proper key schemas
- Uses on-demand billing (PAY_PER_REQUEST)
- Provides detailed status information

### 2. `02_manage_session_records.py`

Provides utilities to manage session records in DynamoDB/CSV.

**Functions:**

#### Delete a Session
Deletes a session record from all related tables and updates Summary_Sessions.

```python
from notebooks.cold_start.02_manage_session_records import delete_session

# Delete a session
delete_session(
    user_id="user123",
    boyfriend_name="John",
    db_write_allowed=True  # Use DynamoDB (False for CSV)
)
```

**Command line:**
```bash
python notebooks/cold_start/02_manage_session_records.py delete <user_id> <boyfriend_name> [--csv]
```

#### Update a Record
Updates a record in a specific table by session_id.

```python
from notebooks.cold_start.02_manage_session_records import update_session_record

# Update a record
update_session_record(
    table_name="session_responses",
    session_id=123456789,
    update_data={"toxic_score": 0.75, "filter_violations": 2},
    db_write_allowed=True
)
```

**Command line:**
```bash
python notebooks/cold_start/02_manage_session_records.py update <table_name> <session_id> --field KEY VALUE [--field KEY VALUE ...] [--csv]
```

#### List Sessions
Lists all sessions or sessions for a specific user.

```python
from notebooks.cold_start.02_manage_session_records import list_sessions

# List all sessions
list_sessions(db_write_allowed=True)

# List sessions for a specific user
list_sessions(user_id="user123", db_write_allowed=True)
```

**Command line:**
```bash
python notebooks/cold_start/02_manage_session_records.py list [--user-id USER_ID] [--csv]
```

## Notes

- All operations automatically update `Summary_Sessions` when records are deleted
- Both notebooks work with both DynamoDB and CSV backends (use `--csv` flag or `db_write_allowed=False`)
- Session IDs are hash-based and generated from `user_id + boyfriend_name` combination
- The delete operation removes records from all related tables:
  - session_responses
  - session_gtk_responses
  - session_feedback
  - session_toxicity_rating
  - session_insights

