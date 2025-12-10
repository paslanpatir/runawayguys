"""Groq API adapter for LLM."""
from typing import Optional, List, Tuple
from src.ports.llm_port import LLMPort
from src.services.insight_prompt_builder import InsightPromptBuilder

try:
    from groq import Groq
except ImportError:
    Groq = None  # Groq package not installed


class GroqAdapter(LLMPort):
    """Groq API implementation of LLMPort."""

    def __init__(self, api_key: str, model_name: str = "llama-3.1-8b-instant"):
        if Groq is None:
            raise ImportError("groq package is not installed. Install it with: pip install groq")
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.provider = "groq"

    def generate_insights(
        self,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        language: str = "EN",
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
    ) -> Optional[str]:
        """
        Generate insights using Groq API.
        """
        try:
            # Build prompt using InsightPromptBuilder
            system_msg, user_prompt = InsightPromptBuilder.build_prompt(
                user_name=user_name,
                bf_name=bf_name,
                toxic_score=toxic_score,
                avg_toxic_score=avg_toxic_score,
                filter_violations=filter_violations,
                violated_filter_questions=violated_filter_questions,
                top_redflag_questions=top_redflag_questions,
                language=language,
            )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_msg
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model=self.model_name,
                temperature=1,  # Match Groq console setting
                max_completion_tokens=150,  # ~100 words (1 token ≈ 0.75 words)
                top_p=1,  # Match Groq console setting
            )

            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"[ERROR] Groq API error: {e}")
            return None

