"""Service for generating insights from survey results using LLM."""
import streamlit as st
from typing import Optional, List, Tuple, Dict, Any
from src.ports.llm_port import LLMPort
from src.adapters.llm.llm_factory import LLMFactory
from src.utils.insight_logger import log_insight_generation


class InsightService:
    """Service for generating insights from survey results."""

    def __init__(self, enabled: bool = True):
        """
        Initialize insight service with LLM adapter.
        
        Args:
            enabled: Whether LLM features are enabled. If False, no LLM will be created.
        """
        self.enabled = enabled
        if enabled:
            self.llm: Optional[LLMPort] = LLMFactory.create()
        else:
            self.llm: Optional[LLMPort] = None

    def generate_survey_insights(
        self,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        language: str = "EN",
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        session_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Generate insights from survey results.
        
        Args:
            user_name: Name of the user
            bf_name: Boyfriend's name
            toxic_score: Toxicity score (0-1)
            avg_toxic_score: Average toxicity score from all users (0-1)
            filter_violations: Number of filter violations
            violated_filter_questions: List of violated filter questions
            language: Language code (TR or EN)
            top_redflag_questions: List of top redflag questions with ratings
            user_id: User ID for logging
            email: User email for logging
            session_data: Full session state for logging
            
        Returns:
            Generated insights text or None if generation fails
        """
        if not self.enabled:
            print("[INFO] LLM features are disabled.")
            return None
        
        if not self.llm:
            print("[WARNING] LLM not configured. Insights generation disabled.")
            return None

        try:
            # Get model name and provider from LLM adapter
            model_name = None
            provider = None
            if hasattr(self.llm, 'model_name'):
                model_name = self.llm.model_name
            if hasattr(self.llm, 'provider'):
                provider = self.llm.provider
            
            # Format model name as "provider: model_name"
            formatted_model_name = None
            if provider and model_name:
                formatted_model_name = f"{provider}: {model_name}"
            elif model_name:
                formatted_model_name = model_name
            
            # Get the prompt text before calling LLM (for logging)
            from src.services.insight_prompt_builder import InsightPromptBuilder
            prompt_text = InsightPromptBuilder.build_full_prompt_text(
                user_name=user_name,
                bf_name=bf_name,
                toxic_score=toxic_score,
                avg_toxic_score=avg_toxic_score,
                filter_violations=filter_violations,
                violated_filter_questions=violated_filter_questions,
                top_redflag_questions=top_redflag_questions,
                language=language,
            )
            
            # Always use English for LLM (better performance)
            # LLM will return English response
            insights = self.llm.generate_insights(
                user_name=user_name,
                bf_name=bf_name,
                toxic_score=toxic_score,
                avg_toxic_score=avg_toxic_score,
                filter_violations=filter_violations,
                violated_filter_questions=violated_filter_questions,
                language="EN",  # Always use English for LLM
                top_redflag_questions=top_redflag_questions,
            )
            
            # Translate English response to Turkish if needed
            if language == "TR" and insights:
                print(f"[DEBUG] Translating insights to Turkish. Original (first 100 chars): {insights[:100]}...")
                translated_insights = self._translate_to_turkish(insights)
                print(f"[DEBUG] Translated (first 100 chars): {translated_insights[:100]}...")
                insights = translated_insights
            
            # Log insight generation for debugging
            if session_data is None:
                session_data = {}
            
            log_insight_generation(
                user_id=user_id or "unknown",
                user_name=user_name,
                email=email,
                bf_name=bf_name,
                language=language,
                toxic_score=toxic_score,
                avg_toxic_score=avg_toxic_score,
                filter_violations=filter_violations,
                violated_filter_questions=violated_filter_questions,
                top_redflag_questions=top_redflag_questions,
                generated_insight=insights,
                prompt_text=prompt_text,
                model_name=formatted_model_name,
                session_data=session_data,
            )
            
            return insights
        except Exception as e:
            print(f"[ERROR] Error generating insights: {e}")
            return None

    def _translate_to_turkish(self, english_text: str) -> str:
        """
        Translate English text to Turkish.
        Uses deep-translator library (Google Translate) if available, otherwise returns English text.
        """
        try:
            from deep_translator import GoogleTranslator
            print("[DEBUG] Initializing GoogleTranslator...")
            translator = GoogleTranslator(source='en', target='tr')
            print(f"[DEBUG] Translating text (length: {len(english_text)})...")
            translated_text = translator.translate(english_text)
            print(f"[DEBUG] Translation successful. Translated text (first 100 chars): {translated_text[:100]}...")
            return translated_text
        except ImportError as e:
            print(f"[WARNING] deep-translator not installed: {e}")
            print("[INFO] Returning English text. For Turkish translation, install deep-translator: pip install deep-translator")
            return english_text
        except Exception as e:
            print(f"[ERROR] Translation failed: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return english_text

    def close(self):
        """Close the LLM connection."""
        if self.llm and hasattr(self.llm, 'close'):
            self.llm.close()

