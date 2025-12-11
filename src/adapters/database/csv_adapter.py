"""CSV adapter implementation."""
import os
import re
import pandas as pd
from src.ports.database_port import DatabasePort
from src.utils.constants import CSV_SEPARATOR


class CSVAdapter(DatabasePort):
    """CSV file implementation of DatabasePort."""

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.data_dir = os.path.join(base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load semicolon-separated CSV from data/."""
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        df = pd.read_csv(file_path, sep=CSV_SEPARATOR)
        
        # Only reorder columns for session response tables that have Q/F columns
        if self._should_reorder_columns(table_name, list(df.columns)):
            reordered_columns = self._reorder_columns(list(df.columns))
            df = df.reindex(columns=reordered_columns)
        
        return df

    def add_record(self, table_name: str, newdata_dict: dict) -> bool:
        """Append record into semicolon-separated CSV in data/.
        
        Preserves column order: if file exists, uses existing column order;
        otherwise uses the order from newdata_dict (Python 3.7+ preserves dict order).
        """
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")

        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path, sep=CSV_SEPARATOR)
            # Get existing columns and reorder them properly
            existing_columns = list(existing_data.columns)
            
            # Create new row with all existing columns, filling missing ones with None
            new_row = {}
            for col in existing_columns:
                new_row[col] = newdata_dict.get(col)
            
            # Add any new columns that don't exist in the file
            for col, val in newdata_dict.items():
                if col not in existing_columns:
                    new_row[col] = val
                    existing_columns.append(col)
            
            # Reorder columns only if this table needs Q/F column reordering
            if self._should_reorder_columns(table_name, existing_columns):
                reordered_columns = self._reorder_columns(existing_columns)
            else:
                reordered_columns = existing_columns
            
            # Create DataFrame with properly ordered columns
            temp = pd.DataFrame([new_row], columns=reordered_columns)
            # Reorder existing data to match
            existing_data = existing_data.reindex(columns=reordered_columns)
            updated_data = pd.concat([existing_data, temp], ignore_index=True)
        else:
            # First record: use the order from newdata_dict, but reorder Q and F columns if needed
            columns_list = list(newdata_dict.keys())
            if self._should_reorder_columns(table_name, columns_list):
                reordered_columns = self._reorder_columns(columns_list)
            else:
                reordered_columns = columns_list
            temp = pd.DataFrame([newdata_dict], columns=reordered_columns)
            updated_data = temp

        updated_data.to_csv(file_path, sep=CSV_SEPARATOR, index=False)
        # Data saved to CSV
        return True

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict) -> None:
        """Update record in semicolon-separated CSV."""
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        df = pd.read_csv(file_path, sep=CSV_SEPARATOR)

        mask = pd.Series(True, index=df.index)
        for k, v in key_dict.items():
            mask &= df[k] == v

        if mask.any():
            for k, v in update_dict.items():
                df.loc[mask, k] = v
            
            # Reorder columns only if this table needs Q/F column reordering
            if self._should_reorder_columns(table_name, list(df.columns)):
                reordered_columns = self._reorder_columns(list(df.columns))
                df = df.reindex(columns=reordered_columns)
            
            df.to_csv(file_path, sep=CSV_SEPARATOR, index=False)
            # Record updated in CSV
        else:
            # No matching record found
            pass

    def delete_record(self, table_name: str, record_id: int, id_column: str = "id") -> bool:
        """Delete a record from CSV by ID."""
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")
        if not os.path.exists(file_path):
            # CSV file not found
            return False

        df = pd.read_csv(file_path, sep=CSV_SEPARATOR)
        
        if id_column not in df.columns:
            # Column not found
            return False

        # Find and delete the record
        initial_count = len(df)
        df = df[df[id_column] != record_id]
        deleted_count = initial_count - len(df)

        if deleted_count > 0:
            df.to_csv(file_path, sep=CSV_SEPARATOR, index=False)
            # Deleted record successfully
            return True
        else:
            # No record found
            return False

    def _should_reorder_columns(self, table_name: str, columns: list) -> bool:
        """
        Check if columns should be reordered for this table.
        Only session response tables with Q/F columns need reordering.
        """
        # Session response tables that have Q/F columns
        session_tables_with_qf = [
            "session_responses",
            "session_gtk_responses",  # Has GTK columns, but we'll check for Q/F
        ]
        
        # Only reorder if it's a session table AND has Q or F columns
        if table_name in session_tables_with_qf:
            # Check if table has Q or F columns
            has_q_columns = any(col.startswith('Q') and len(col) > 1 and col[1:].isdigit() for col in columns)
            has_f_columns = any(col.startswith('F') and len(col) > 1 and col[1:].isdigit() for col in columns)
            return has_q_columns or has_f_columns
        
        return False
    
    def _reorder_columns(self, columns: list) -> list:
        """
        Reorder columns to ensure Q1-Q75 and F1-F15 are in numerical order.
        
        Args:
            columns: List of column names
            
        Returns:
            Reordered list with Q and F columns in numerical order
        """
        # Separate columns into different groups
        other_cols = []
        q_cols = []
        f_cols = []
        
        for col in columns:
            if col.startswith('Q') and len(col) > 1:
                # Extract number from Q columns (Q1, Q2, ..., Q75)
                match = re.match(r'Q(\d+)', col)
                if match:
                    q_cols.append((int(match.group(1)), col))
            elif col.startswith('F') and len(col) > 1:
                # Extract number from F columns (F1, F2, ..., F15)
                match = re.match(r'F(\d+)', col)
                if match:
                    f_cols.append((int(match.group(1)), col))
            else:
                other_cols.append(col)
        
        # Sort Q and F columns by their numeric value
        q_cols.sort(key=lambda x: x[0])
        f_cols.sort(key=lambda x: x[0])
        
        # Extract just the column names in order
        q_col_names = [col for _, col in q_cols]
        f_col_names = [col for _, col in f_cols]
        
        # Build result with proper order:
        # id, user_id, name, email, boyfriend_name, language, toxic_score,
        # Q1-Q75, F1-F15, filter_violations, timestamps, other columns
        result = []
        
        # Add non-Q/F columns in their original order, but insert Q and F at the right places
        for col in other_cols:
            # Insert Q columns after toxic_score
            if col == 'toxic_score' and q_col_names:
                result.append(col)
                result.extend(q_col_names)
            # Insert F columns before filter_violations
            elif col == 'filter_violations' and f_col_names:
                result.extend(f_col_names)
                result.append(col)
            else:
                result.append(col)
        
        # If Q columns weren't inserted (toxic_score not found), insert after language or at end of basic columns
        if q_col_names and not any(col.startswith('Q') for col in result):
            # Find position after toxic_score or language
            insert_pos = len(result)
            for i, col in enumerate(result):
                if col in ['toxic_score', 'language']:
                    insert_pos = i + 1
                    break
            result[insert_pos:insert_pos] = q_col_names
        
        # If F columns weren't inserted, insert before filter_violations or after Q columns
        if f_col_names and not any(col.startswith('F') for col in result):
            # Find position before filter_violations or after last Q column
            insert_pos = len(result)
            for i, col in enumerate(result):
                if col == 'filter_violations':
                    insert_pos = i
                    break
                # If we've passed all Q columns, insert here
                if col.startswith('Q') and i < len(result) - 1:
                    if not result[i+1].startswith('Q'):
                        insert_pos = i + 1
            result[insert_pos:insert_pos] = f_col_names
        
        return result

    def close(self) -> None:
        """No-op for CSV adapter."""
        pass

