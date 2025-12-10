"""LLM connection manager - handles loading LLM API credentials."""
import os

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip


class LLMConnectionManager:
    """Manages LLM API connection credentials."""

    def __init__(self, secret_file="config/llm_credentials.txt"):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.secret_file = os.path.join(base_dir, secret_file)
        self.provider = None
        self.api_key = None
        self.model_name = None

    def load_credentials(self):
        """Load LLM credentials from env vars or fallback file."""
        # Try Hugging Face first
        hf_token = os.getenv("HF_API_TOKEN")
        groq_key = os.getenv("GROQ_API_KEY")
        
        if hf_token:
            self.provider = "huggingface"
            self.api_key = hf_token
            self.model_name = os.getenv("HF_MODEL", "gpt2")
            print("[OK] Running with Hugging Face API (env credentials found)")
            return
        
        if groq_key:
            self.provider = "groq"
            self.api_key = groq_key
            self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            print("[OK] Running with Groq API (env credentials found)")
            return
        
        # Try loading from file
        print(f"[INFO] Running locally, looking for LLM credentials in file: {self.secret_file}")
        try:
            with open(self.secret_file, "r", encoding="utf-8") as file:
                lines = [
                    line.strip()
                    for line in file.readlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                print(f"[DEBUG] Found {len(lines)} non-comment lines in credentials file")
                if len(lines) >= 2:
                    self.provider = lines[0].lower().strip()  # huggingface or groq
                    self.api_key = lines[1].strip()
                    self.model_name = lines[2].strip() if len(lines) > 2 and lines[2].strip() else None
                    print(f"[OK] Loaded LLM credentials: provider={self.provider}, model={self.model_name}")
                else:
                    print(f"[ERROR] File has insufficient lines. Found {len(lines)} lines, need at least 2 (provider and API key)")
                    raise ValueError("File is missing required credentials!")
        except FileNotFoundError:
            print(f"[WARNING] LLM credentials file not found at: {self.secret_file}")
            print("[WARNING] LLM features will be disabled.")
            self.provider = None
            self.api_key = None
            return
        except Exception as e:
            print(f"[ERROR] Error loading LLM credentials: {e}")
            raise RuntimeError(f"Error loading LLM credentials: {e}")

    def get_credentials(self):
        """Get LLM credentials, loading if necessary."""
        if not self.api_key:
            self.load_credentials()
        return {
            "provider": self.provider,
            "api_key": self.api_key,
            "model_name": self.model_name,
        }

    def close(self):
        """Close/reset connection."""
        self.provider = None
        self.api_key = None
        self.model_name = None
        print("[CLOSED] LLM connection manager closed")

