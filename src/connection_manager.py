import os
import boto3

class ConnectionManager:
    def __init__(self, secret_file="config/aws_credentials.txt"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.secret_file = os.path.join(base_dir, secret_file)
        self.access_key = None
        self.secret_key = None
        self.region_name = None
        self.session = None
        self.dynamodb = None

    def load_credentials(self):
        """Load AWS credentials from env vars or fallback file."""
        access_code = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key  = os.getenv("AWS_SECRET_ACCESS_KEY")
        region_name = os.getenv("AWS_DEFAULT_REGION")

        if access_code and secret_key and region_name:
            print("[OK] Running in app service (env credentials found)")
        else:
            print("[INFO] Running locally, looking for credentials in file")
            try:
                with open(self.secret_file, "r") as file:
                    access_code = file.readline().strip()
                    secret_key  = file.readline().strip()
                    region_name = file.readline().strip()
                if not access_code or not secret_key:
                    raise ValueError("File is missing credentials!")
            except FileNotFoundError:
                raise FileNotFoundError(f"Error: {self.secret_file} not found.")
            except Exception as e:
                raise RuntimeError(f"Error loading credentials: {e}")

        self.access_key = access_code
        self.secret_key = secret_key
        self.region_name = region_name

    def connect(self):
        """Establish boto3 session and DynamoDB resource."""
        if not self.access_key:
            self.load_credentials()

        self.session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name
        )
        self.dynamodb = self.session.resource("dynamodb")
        print("[OK] AWS DynamoDB connection established")
        return self.dynamodb

    def close(self):
        """Close the session and release resources."""
        self.session = None
        self.dynamodb = None
        print("[CLOSED] AWS DynamoDB connection closed")