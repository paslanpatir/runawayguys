"""Factory for creating LLM adapters."""
from typing import Optional
from src.ports.llm_port import LLMPort
from src.infrastructure.llm_connection_manager import LLMConnectionManager
from src.adapters.llm.huggingface_adapter import HuggingFaceAdapter
from src.adapters.llm.groq_adapter import GroqAdapter


class LLMFactory:
    """Factory for creating LLM adapters based on configuration."""

    @staticmethod
    def create() -> Optional[LLMPort]:
        """
        Create appropriate LLM adapter based on configuration.
        
        Returns:
            LLM adapter instance or None if not configured
        """
        conn_manager = LLMConnectionManager()
        credentials = conn_manager.get_credentials()

        provider = credentials.get("provider")
        api_key = credentials.get("api_key")
        model_name = credentials.get("model_name")

        print(f"[DEBUG] LLM Factory - provider: {provider}, api_key present: {bool(api_key)}, model: {model_name}")

        if not provider or not api_key:
            print("[INFO] LLM not configured. Set HF_API_TOKEN or GROQ_API_KEY environment variables or configure config/llm_credentials.txt")
            return None

        if provider == "huggingface":
            return HuggingFaceAdapter(
                api_key=api_key,
                model_name=model_name or "gpt2"
            )
        elif provider == "groq":
            try:
                return GroqAdapter(
                    api_key=api_key,
                    model_name=model_name or "llama-3.1-8b-instant"
                )
            except ImportError:
                print("[ERROR] groq package not installed. Install it with: pip install groq")
                return None
        else:
            print(f"[WARNING] Unknown LLM provider: {provider}")
            return None

