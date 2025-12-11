# Testing DynamoDB Flow

## Prerequisites

1. **AWS Credentials**: Make sure `config/aws_credentials.txt` is set up with:
   - AWS Access Key ID
   - AWS Secret Access Key  
   - AWS Region

2. **Configuration**: In the notebook, set:
   ```python
   USE_DYNAMODB = True
   ```

## Testing Steps

### 1. List Sessions
First, list all sessions to see what's available:
```python
list_sessions(db_write_allowed=USE_DYNAMODB)
```

This will show you all sessions with their `id` values (session IDs).

### 2. Delete a Session
Use the `id` value from the list above:
```python
delete_session(
    session_id=123456789,  # Replace with actual session_id from list_sessions()
    db_write_allowed=USE_DYNAMODB
)
```

**What it does:**
- Deletes the record from all related tables:
  - `session_responses`
  - `session_gtk_responses`
  - `session_feedback`
  - `session_toxicity_rating`
  - `session_insights`
- Updates `Summary_Sessions` table automatically

### 3. Verify Deletion
Run `list_sessions()` again to confirm the session was deleted.

### 4. Update a Record (Optional)
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

## Expected Output

When deleting a session, you should see:
```
============================================================
Deleting Session Record
============================================================
Session ID: 123456789
Backend: DynamoDB
============================================================

[1] Loading record with session_id 123456789 from session_responses...
[OK] Found record:
     Session ID: 123456789
     User ID: ...
     Boyfriend Name: ...
     Toxic Score: ...
     Filter Violations: ...

[2] Deleting records with session_id 123456789 from all tables...
[OK] Deleted from session_responses
[OK] Deleted from session_gtk_responses
[OK] Deleted from session_feedback
[OK] Deleted from session_toxicity_rating
[INFO] No record found in session_insights (may not exist for this session)

[3] Updating Summary_Sessions...
[OK] Updated Summary_Sessions after delete. New count_guys: X, avg_toxic_score: Y.YYYY

============================================================
[SUCCESS] Session record deleted and Summary_Sessions updated!
============================================================
```

## Troubleshooting

### Error: "Float types are not supported. Use Decimal types instead."
- **Fixed!** This was a bug in `summary_updater.py` that has been corrected.
- The function now uses `Decimal` types for all numeric values when updating DynamoDB.

### Error: "Record with session_id=X not found"
- Make sure you're using the correct `id` value from `list_sessions()` output
- The `id` is an integer (not a string hash)

### Error: "AWS DynamoDB connection failed"
- Check your `config/aws_credentials.txt` file
- Verify AWS credentials are correct
- Make sure the AWS region is correct

## Notes

- Session IDs are integers (generated from hash of user_id + boyfriend_name)
- The `id` column in all tables stores the session_id as a number
- When deleting, the `Summary_Sessions` table is automatically updated
- All operations are idempotent (safe to run multiple times)

