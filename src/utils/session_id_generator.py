"""Utility functions for generating unique session IDs based on user_id and boyfriend_name."""
import hashlib


def generate_session_id(user_id: str, boyfriend_name: str) -> int:
    """
    Generate a unique, deterministic session_id based on user_id and boyfriend_name.
    
    This ensures that:
    - Same user_id + boyfriend_name always produces the same session_id
    - Different combinations produce different session_ids
    - IDs are order-agnostic (don't depend on insertion order)
    
    Args:
        user_id: Unique identifier for the user
        boyfriend_name: Name of the boyfriend being rated
        
    Returns:
        A positive integer session_id
    """
    # Create a deterministic string from user_id and boyfriend_name
    # Normalize by converting to lowercase and stripping whitespace
    combined = f"{user_id.lower().strip()}_{boyfriend_name.lower().strip()}"
    
    # Generate hash using SHA256 for better distribution
    hash_obj = hashlib.sha256(combined.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # Convert first 8 characters of hash to integer (ensures positive number)
    # Using modulo to keep it within reasonable range (max ~4.3 billion)
    session_id = int(hash_hex[:8], 16) % (2**31 - 1)  # Max 32-bit signed integer
    
    # Ensure it's positive and at least 1
    if session_id == 0:
        session_id = 1
    
    return session_id


def find_existing_session_id(
    db_handler,
    table_name: str,
    user_id: str,
    boyfriend_name: str,
) -> int:
    """
    Find existing session_id for a user_id + boyfriend_name combination.
    
    Args:
        db_handler: DatabaseHandler instance
        table_name: Name of the table to search
        user_id: User ID to search for
        boyfriend_name: Boyfriend name to search for
        
    Returns:
        Existing session_id if found, None otherwise
    """
    try:
        existing = db_handler.load_table(table_name)
        if existing.empty:
            return None
        
        # Search for matching user_id and boyfriend_name
        mask = (existing["user_id"] == user_id) & (existing["boyfriend_name"] == boyfriend_name)
        matching = existing[mask]
        
        if not matching.empty:
            # Return the first matching ID
            return int(matching.iloc[0]["id"])
        
        return None
    except Exception as e:
        print(f"[WARNING] Could not search for existing session_id: {e}")
        return None


def get_or_create_session_id(
    db_handler,
    table_name: str,
    user_id: str,
    boyfriend_name: str,
) -> int:
    """
    Get existing session_id or generate a new one.
    
    First checks if a record with the same user_id + boyfriend_name exists.
    If found, returns that session_id. Otherwise, generates a new one.
    
    Args:
        db_handler: DatabaseHandler instance
        table_name: Name of the table to check
        user_id: User ID
        boyfriend_name: Boyfriend name
        
    Returns:
        Session ID (either existing or newly generated)
    """
    # First, try to find existing session_id
    existing_id = find_existing_session_id(db_handler, table_name, user_id, boyfriend_name)
    
    if existing_id is not None:
        print(f"[INFO] Found existing session_id {existing_id} for user_id={user_id}, boyfriend_name={boyfriend_name}")
        return existing_id
    
    # Generate new session_id
    new_id = generate_session_id(user_id, boyfriend_name)
    print(f"[INFO] Generated new session_id {new_id} for user_id={user_id}, boyfriend_name={boyfriend_name}")
    
    # Check if this ID already exists (collision check)
    try:
        existing = db_handler.load_table(table_name)
        if not existing.empty:
            if new_id in existing["id"].values:
                # Collision detected - append a counter
                counter = 1
                while new_id + counter in existing["id"].values:
                    counter += 1
                new_id = new_id + counter
                print(f"[WARNING] Session ID collision detected, using {new_id} instead")
    except Exception:
        pass  # If we can't check, just use the generated ID
    
    return new_id

