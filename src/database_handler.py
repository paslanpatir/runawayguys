import os
import pandas as pd
from src.connection_manager import ConnectionManager


class DynamoDBHandler:
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

        return pd.DataFrame(items).reset_index(drop=True)

    def add_record(self, table_name: str, newdata_dict: dict) -> bool:
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=newdata_dict)
            print(f"[OK] Data written to DynamoDB: {table_name}")
            return True
        except Exception as e:
            print(f"[ERROR] Error writing to DynamoDB: {e}")
            return False

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict):
        try:
            table = self.dynamodb.Table(table_name)
            update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in update_dict.keys())
            expression_attribute_values = {f":{k}": v for k, v in update_dict.items()}
            table.update_item(
                Key=key_dict,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
            print(f"[OK] DynamoDB record updated in {table_name}")
        except Exception as e:
            print(f"[ERROR] Error updating DynamoDB record: {e}")

    def close(self):
        self.conn_manager.close()



class CSVHandler:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load semicolon-separated CSV from data/."""
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        return pd.read_csv(file_path, sep=";")

    def add_record(self, table_name: str, newdata_dict: dict) -> bool:
        """Append record into semicolon-separated CSV in data/."""
        file_path = os.path.join(self.data_dir, f"{table_name}.csv")
        temp = pd.DataFrame([newdata_dict])

        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path, sep=";")
            updated_data = pd.concat([existing_data, temp], ignore_index=True)
        else:
            updated_data = temp

        updated_data.to_csv(file_path, sep=";", index=False)
        print(f"[OK] Data saved to CSV: {file_path}")
        return True

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict):
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

class DatabaseHandler:
    def __init__(self, db_read_allowed=False, db_write_allowed=False):
        if db_read_allowed or db_write_allowed:
            self.backend = DynamoDBHandler()
        else:
            self.backend = CSVHandler()

    def load_table(self, table_name: str):
        return self.backend.load_table(table_name)

    def add_record(self, table_name: str, newdata_dict: dict):
        return self.backend.add_record(table_name, newdata_dict)

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict):
        return self.backend.update_record(table_name, key_dict, update_dict)

    def close(self):
        if isinstance(self.backend, DynamoDBHandler):
            self.backend.close()
