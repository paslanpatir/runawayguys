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

### 2. `02_manage_session_records.ipynb` (DEPRECATED)

**Note:** This notebook has been split into multiple specialized notebooks (03-08). Use the new notebooks instead.

### 3. `03_initialize_tables.ipynb`

Initializes all CSV files and/or database tables with default values.

**Use this when:**
- Setting up a new environment
- After clearing all session data
- When Summary_Sessions table is empty or missing

**What it does:**
- Initializes `Summary_Sessions` table/file with default values
- Works with both DynamoDB and CSV backends

**Usage:**
1. Set `USE_DYNAMODB = True` or `False` in the configuration cell
2. Uncomment and run the initialization cell:
```python
initialize_summary_sessions_manual(use_dynamodb=USE_DYNAMODB)
```

### 4. `04_delete_session.ipynb`

Deletes a session record from all related tables by session_id and updates Summary_Sessions.

**Usage:**
1. Set `USE_DYNAMODB = True` or `False` in the configuration cell
2. Get the session_id from `list_sessions()` output (see `06_list_sessions.ipynb`)
3. Uncomment and modify the example cell:
```python
delete_session(
    session_id="12",  # This is the 'id' column value from the table
    db_write_allowed=USE_DYNAMODB
)
```

**Note:** 
- The `session_id` parameter is the value stored in the `id` column in all database tables
- This value is a hash of user_id and boyfriend_name
- You can get it from the `list_sessions()` function output

### 5. `05_update_session.ipynb`

Updates a record in a specific table by session_id.

**Usage:**
1. Set `USE_DYNAMODB = True` or `False` in the configuration cell
2. Uncomment and modify the example cell:
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

### 6. `06_list_sessions.ipynb`

Lists all sessions or sessions for a specific user.

**Usage:**
1. Set `USE_DYNAMODB = True` or `False` in the configuration cell
2. To list all sessions, run:
```python
list_sessions(db_write_allowed=USE_DYNAMODB)
```

3. To list sessions for a specific user, uncomment and modify:
```python
list_sessions(user_id="your_user_id_here", db_write_allowed=USE_DYNAMODB)
```

### 7. `07_reassign_session_ids.ipynb`

Reassigns session IDs based on (user_id, test_date, boyfriend_name) combination and recalculates Summary_Sessions.

**Use this when:**
- Session IDs are inconsistent across tables
- You need to fix session ID assignments based on user_id, test_date, and boyfriend_name
- You want to recalculate Summary_Sessions from scratch

**What it does:**
1. Groups records by (user_id, test_date, boyfriend_name) combination
2. Assigns the same session_id to all records with matching combinations across all CSV files
3. Recalculates Summary_Sessions based on the updated data

**Usage:**
1. First run with `dry_run=True` to preview changes:
```python
reassign_session_ids_and_recalculate(dry_run=True)
```

2. Then set `dry_run=False` to apply changes:
```python
reassign_session_ids_and_recalculate(dry_run=False)
```

**Note:** This notebook works with CSV files only (not DynamoDB).

### 8. `08_clear_all_data.ipynb`

**WARNING:** This will delete ALL records from all session_* tables and CSV files. This action cannot be undone!

**Use this when:**
- You want to start fresh with clean data
- You need to reset all session data
- After testing or development

**What it does:**
1. Deletes all records from session_* tables in DynamoDB (if enabled)
2. Deletes all session_*.csv files from the data folder
3. Clears Summary_Sessions table/file

**Note:** Question files (GetToKnowQuestions.csv, RedFlagQuestions.csv, etc.) are NOT affected.

**Usage:**
1. Set `USE_DYNAMODB = True` or `False` in the configuration cell
2. Uncomment and set `confirm=True` to proceed:
```python
clear_all_session_data(use_dynamodb=USE_DYNAMODB, confirm=True)
```

## General Notes

- All operations automatically update `Summary_Sessions` when records are deleted
- Most notebooks work with both DynamoDB and CSV backends (set `USE_DYNAMODB` configuration)
- Session IDs are hash-based and generated from `user_id + boyfriend_name + test_date` combination
- The delete operation removes records from all related tables:
  - session_responses
  - session_gtk_responses
  - session_feedback
  - session_toxicity_rating
  - session_insights

## Workflow Examples

### Starting Fresh
1. Run `01_initialize_dynamodb_tables.ipynb` to create tables (if using DynamoDB)
2. Run `08_clear_all_data.ipynb` to clear any existing data
3. Run `03_initialize_tables.ipynb` to initialize Summary_Sessions with defaults

### Managing Sessions
1. Use `06_list_sessions.ipynb` to view all sessions and find session IDs
2. Use `04_delete_session.ipynb` to delete a specific session
3. Use `05_update_session.ipynb` to update a record in a specific table

### Fixing Session IDs
1. Use `07_reassign_session_ids.ipynb` to reassign session IDs based on (user_id, test_date, boyfriend_name)
2. This will also recalculate Summary_Sessions automatically

