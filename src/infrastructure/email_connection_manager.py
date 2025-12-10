"""Email connection manager - handles loading email credentials."""
import os

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip


class EmailConnectionManager:
    """Manages email SMTP connection credentials."""

    def __init__(self, secret_file="config/email_credentials.txt"):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.secret_file = os.path.join(base_dir, secret_file)
        self.smtp_server = None
        self.smtp_port = None
        self.sender_email = None
        self.sender_password = None

    def load_credentials(self):
        """Load email credentials from env vars or fallback file."""
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT")
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if smtp_server and sender_email and sender_password:
            print("[OK] Running in app service (env email credentials found)")
        else:
            print("[INFO] Running locally, looking for email credentials in file")
            try:
                with open(self.secret_file, "r") as file:
                    lines = [
                        line.strip()
                        for line in file.readlines()
                        if line.strip() and not line.strip().startswith("#")
                    ]
                    if len(lines) >= 4:
                        smtp_server = lines[0] if not smtp_server else smtp_server
                        smtp_port = lines[1] if not smtp_port else smtp_port
                        sender_email = lines[2] if not sender_email else sender_email
                        sender_password = lines[3] if not sender_password else sender_password
                    elif len(lines) >= 3:
                        # Handle case where port might be missing
                        smtp_server = lines[0] if not smtp_server else smtp_server
                        sender_email = lines[1] if not sender_email else sender_email
                        sender_password = lines[2] if not sender_password else sender_password
                    else:
                        raise ValueError("File is missing required credentials!")
            except FileNotFoundError:
                raise FileNotFoundError(f"Error: {self.secret_file} not found.")
            except Exception as e:
                raise RuntimeError(f"Error loading email credentials: {e}")

        self.smtp_server = smtp_server or "smtp.gmail.com"
        self.smtp_port = int(smtp_port) if smtp_port else 587
        self.sender_email = sender_email
        self.sender_password = sender_password

    def get_credentials(self):
        """Get email credentials, loading if necessary."""
        if not self.sender_email:
            self.load_credentials()
        return {
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "sender_email": self.sender_email,
            "sender_password": self.sender_password,
        }

    def close(self):
        """Close/reset connection (for consistency with ConnectionManager)."""
        self.smtp_server = None
        self.smtp_port = None
        self.sender_email = None
        self.sender_password = None
        print("[CLOSED] Email connection manager closed")

