"""
Notebook: Initialize All DynamoDB Output Tables

This notebook initializes all DynamoDB tables needed for the Runaway Guys application.
Run this once when setting up a new DynamoDB environment or when you need to recreate tables.

Tables initialized:
- session_responses: Main survey responses
- session_gtk_responses: Get-to-know questions responses
- session_feedback: User feedback ratings
- session_toxicity_rating: Toxicity opinion ratings
- session_insights: AI-generated insights metadata
- Summary_Sessions: Aggregated statistics across all sessions
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.connection_manager import ConnectionManager
from botocore.exceptions import ClientError


def create_table_if_not_exists(dynamodb, table_name, key_schema, attribute_definitions, billing_mode='PAY_PER_REQUEST'):
    """
    Create a DynamoDB table if it doesn't already exist.
    
    Args:
        dynamodb: DynamoDB resource
        table_name: Name of the table
        key_schema: Key schema definition
        attribute_definitions: Attribute definitions
        billing_mode: Billing mode ('PAY_PER_REQUEST' or 'PROVISIONED')
        
    Returns:
        True if table exists or was created, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Table: {table_name}")
    print(f"{'='*60}")
    
    try:
        # Check if table already exists
        table = dynamodb.Table(table_name)
        table.load()
        print(f"[INFO] Table '{table_name}' already exists")
        print(f"       Status: {table.table_status}")
        
        # Get table details
        table_description = table.meta.client.describe_table(TableName=table_name)
        item_count = table_description['Table'].get('ItemCount', 0)
        print(f"       Item Count: {item_count}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"[INFO] Table '{table_name}' does not exist, creating...")
            
            try:
                # Create table
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attribute_definitions,
                    BillingMode=billing_mode
                )
                
                # Wait for table to be created
                print(f"[INFO] Waiting for table '{table_name}' to be created...")
                table.wait_until_exists()
                
                print(f"[OK] Table '{table_name}' created successfully!")
                
                # Get table details
                table_description = table.meta.client.describe_table(TableName=table_name)
                print(f"       Status: {table_description['Table']['TableStatus']}")
                print(f"       Billing Mode: {table_description['Table'].get('BillingModeSummary', {}).get('BillingMode', 'N/A')}")
                
                return True
                
            except Exception as create_error:
                print(f"[ERROR] Failed to create table '{table_name}': {create_error}")
                return False
        else:
            print(f"[ERROR] Error checking table '{table_name}': {e}")
            return False


def initialize_all_tables():
    """Initialize all DynamoDB tables for the application."""
    print("="*60)
    print("Initializing All DynamoDB Tables")
    print("="*60)
    
    try:
        # Connect to DynamoDB
        conn_manager = ConnectionManager()
        dynamodb = conn_manager.connect()
        
        tables_created = 0
        tables_existing = 0
        
        # Define all tables with their schemas
        tables_config = [
            {
                "name": "session_responses",
                "key_schema": [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                "attribute_definitions": [
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'N'  # Number
                    }
                ]
            },
            {
                "name": "session_gtk_responses",
                "key_schema": [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                "attribute_definitions": [
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'N'
                    }
                ]
            },
            {
                "name": "session_feedback",
                "key_schema": [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                "attribute_definitions": [
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'N'
                    }
                ]
            },
            {
                "name": "session_toxicity_rating",
                "key_schema": [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                "attribute_definitions": [
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'N'
                    }
                ]
            },
            {
                "name": "session_insights",
                "key_schema": [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                "attribute_definitions": [
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'N'
                    }
                ]
            },
            {
                "name": "Summary_Sessions",
                "key_schema": [
                    {
                        'AttributeName': 'summary_id',
                        'KeyType': 'HASH'
                    }
                ],
                "attribute_definitions": [
                    {
                        'AttributeName': 'summary_id',
                        'AttributeType': 'N'
                    }
                ]
            }
        ]
        
        # Create all tables
        for table_config in tables_config:
            table_name = table_config["name"]
            key_schema = table_config["key_schema"]
            attribute_definitions = table_config["attribute_definitions"]
            
            # Check if table exists before creating
            try:
                existing_table = dynamodb.Table(table_name)
                existing_table.load()
                result = True
                tables_existing += 1
            except ClientError:
                result = create_table_if_not_exists(
                    dynamodb, table_name, key_schema, attribute_definitions
                )
                if result:
                    tables_created += 1
        
        conn_manager.close()
        
        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Tables already existing: {tables_existing}")
        print(f"Tables created: {tables_created}")
        print(f"Total tables: {len(tables_config)}")
        print("="*60)
        
        if tables_created > 0:
            print("\n[SUCCESS] All tables initialized successfully!")
        else:
            print("\n[INFO] All tables already exist. No new tables created.")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error initializing tables: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = initialize_all_tables()
    sys.exit(0 if success else 1)

