"""DynamoDB adapter implementation."""
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

    def update_record(self, table_name: str, key_dict: dict, update_dict: dict) -> None:
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

    def close(self) -> None:
        self.conn_manager.close()

