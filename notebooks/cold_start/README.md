# Cold Start Notebooks

This folder contains Jupyter notebooks for initializing and managing DynamoDB tables.

## Notebooks

### 1. `01_initialize_dynamodb_tables.ipynb`

Initializes all DynamoDB output tables needed for the Runaway Guys application.

**Tables initialized:**
- `session_responses` - Main survey responses
- `session_gtk_responses` - Get-to-know questions responses
- `session_feedback` - User feedback ratings
- `session_toxicity_rating` - Toxicity opinion ratings
- `session_insights` - AI-generated insights metadata
- `Summary_Sessions` - Aggregated statistics across all sessions

**Usage:**
1. Open the notebook in Jupyter Lab/Notebook
2. Run all cells sequentially
3. The notebook will check if tables exist and create them if needed

**Features:**
- Checks if tables already exist (won't recreate existing tables)
- Creates tables with proper key schemas
- Uses on-demand billing (PAY_PER_REQUEST)
- Provides detailed status information

### 2. `02_manage_session_records.ipynb`

Provides utilities to manage session records in DynamoDB/CSV.

**Functions:**

#### Delete a Session
Deletes a session record from all related tables by session_id and updates Summary_Sessions.

1. Set `USE_DYNAMODB = True` or `False` in the configuration cell
2. Get the session_id from `list_sessions()` output (shown as "Session ID")
3. Uncomment and modify the example cell:
```python
delete_session(
    session_id="your_session_id_here",  # This is the 'id' column value from the table
    db_write_allowed=USE_DYNAMODB
)
```

**Note:** 
- The `session_id` parameter is the value stored in the `id` column in all database tables
- This value is a hash of user_id and boyfriend_name
- You can get it from the `list_sessions()` function output

#### Update a Record
Updates a record in a specific table by session_id.

1. Uncomment and modify the example cell:
```python
update_session_record(
    table_name="session_responses",
    session_id=123456789,
    update_data={
        "toxic_score": 0.75,
        "filter_violations": 2
    },
    db_write_allowed=USE_DYNAMODB
)
```

#### List Sessions
Lists all sessions or sessions for a specific user.

1. To list all sessions, run the cell with:
```python
list_sessions(db_write_allowed=USE_DYNAMODB)
```

2. To list sessions for a specific user, uncomment and modify:
```python
list_sessions(user_id="your_user_id_here", db_write_allowed=USE_DYNAMODB)
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

