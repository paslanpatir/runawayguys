"""CSV adapter implementation."""
import os
import pandas as pd
from src.ports.database_port import DatabasePort


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

        return pd.read_csv(file_path, sep=";")

    def add_record(self, table_name: str, newdata_dict: dict) -> bool:
        """Append record into semicolon-separated CSV in data/.
        
        Preserves column order: if file exists, uses existing column order;
        otherwise uses the order from newdata_dict (Python 3.7+ preserves dict order).
        """
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")

        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path, sep=";")
            # Preserve existing column order
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
            
            # Create DataFrame with preserved column order
            temp = pd.DataFrame([new_row], columns=existing_columns)
            updated_data = pd.concat([existing_data, temp], ignore_index=True)
        else:
            # First record: use the order from newdata_dict
            # Python 3.7+ preserves dict insertion order
            temp = pd.DataFrame([newdata_dict])
            updated_data = temp

        updated_data.to_csv(file_path, sep=";", index=False)
        print(f"[OK] Data saved to CSV: {file_path}")
        return True

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict) -> None:
        """Update record in semicolon-separated CSV."""
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        df = pd.read_csv(file_path, sep=";")

        mask = pd.Series(True, index=df.index)
        for k, v in key_dict.items():
            mask &= df[k] == v

        if mask.any():
            for k, v in update_dict.items():
                df.loc[mask, k] = v
            df.to_csv(file_path, sep=";", index=False)
            print(f"[OK] Record updated in CSV: {file_path}")
        else:
            print(f"[WARNING] No matching record found in {file_path} for key {key_dict}")

    def close(self) -> None:
        """No-op for CSV adapter."""
        pass

