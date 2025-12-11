"""DynamoDB adapter implementation."""
import re
import pandas as pd
from src.infrastructure.connection_manager import ConnectionManager
from src.ports.database_port import DatabasePort


class DynamoDBAdapter(DatabasePort):
    """DynamoDB implementation of DatabasePort."""

    def __init__(self):
        self.conn_manager = ConnectionManager()
        self.dynamodb = self.conn_manager.connect()

    def load_table(self, table_name: str) -> pd.DataFrame:
        table = self.dynamodb.Table(table_name)
        response = table.scan()
        items = response["Items"]

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response["Items"])

        df = pd.DataFrame(items).reset_index(drop=True)
        
        # Only reorder columns for session response tables that have Q/F columns
        if not df.empty and self._should_reorder_columns(table_name, list(df.columns)):
            reordered_columns = self._reorder_columns(list(df.columns))
            df = df.reindex(columns=reordered_columns)
        
        return df

    def add_record(self, table_name: str, newdata_dict: dict) -> bool:
        try:
            # Reorder dictionary keys only for session response tables with Q/F columns
            if self._should_reorder_columns(table_name, list(newdata_dict.keys())):
                reordered_dict = self._reorder_dict_keys(newdata_dict)
            else:
                reordered_dict = newdata_dict
            
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=reordered_dict)
            # Data written to DynamoDB
            return True
        except Exception as e:
            # Error writing to DynamoDB
            return False

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict) -> None:
        try:
            # Reorder dictionary keys only for session response tables with Q/F columns
            if self._should_reorder_columns(table_name, list(update_dict.keys())):
                reordered_update_dict = self._reorder_dict_keys(update_dict)
            else:
                reordered_update_dict = update_dict
            
            table = self.dynamodb.Table(table_name)
            update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in reordered_update_dict.keys())
            expression_attribute_values = {f":{k}": v for k, v in reordered_update_dict.items()}
            table.update_item(
                Key=key_dict,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
            # DynamoDB record updated
        except Exception as e:
            # Error updating DynamoDB record
            pass

    def delete_record(self, table_name: str, record_id: int, id_column: str = "id") -> bool:
        """Delete a record from DynamoDB by ID.
        
        Note: For DynamoDB, the primary key must be specified correctly.
        Most tables use 'id' as the partition key.
        """
        try:
            table = self.dynamodb.Table(table_name)
            # DynamoDB requires the full primary key
            # For most tables, the primary key is just 'id'
            key_dict = {id_column: record_id}
            
            # First, check if the record exists by trying to get it
            try:
                response = table.get_item(Key=key_dict)
                if "Item" not in response:
                    # No record found
                    return False
            except Exception as e:
                # Could not check if record exists
                return False
            
            # Delete the record
            table.delete_item(Key=key_dict)
            # Deleted record successfully
            return True
        except Exception as e:
            # Error deleting DynamoDB record
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
    
    def _reorder_dict_keys(self, data_dict: dict) -> dict:
        """
        Reorder dictionary keys to ensure Q and F columns are in numerical order.
        
        Args:
            data_dict: Dictionary with potentially unordered Q/F keys
            
        Returns:
            Dictionary with Q and F keys in numerical order
        """
        if not data_dict:
            return data_dict
        
        # Get all keys
        keys = list(data_dict.keys())
        
        # Reorder keys using the same logic as _reorder_columns
        reordered_keys = self._reorder_columns(keys)
        
        # Create new dictionary with reordered keys
        return {key: data_dict[key] for key in reordered_keys if key in data_dict}

    def close(self) -> None:
        self.conn_manager.close()

