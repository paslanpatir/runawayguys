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
            # Get model name from LLM adapter
            model_name = None
            if hasattr(self.llm, 'model_name'):
                model_name = self.llm.model_name
            
            # Get the prompt text before calling LLM (for logging)
            prompt_text = self._get_prompt_text(
                user_name, bf_name, toxic_score, avg_toxic_score,
                filter_violations, violated_filter_questions, language, top_redflag_questions
            )
            
            insights = self.llm.generate_insights(
                user_name=user_name,
                bf_name=bf_name,
                toxic_score=toxic_score,
                avg_toxic_score=avg_toxic_score,
                filter_violations=filter_violations,
                violated_filter_questions=violated_filter_questions,
                language=language,
                top_redflag_questions=top_redflag_questions,
            )
            
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
                model_name=model_name,
                session_data=session_data,
            )
            
            return insights
        except Exception as e:
            print(f"[ERROR] Error generating insights: {e}")
            return None

    def _get_prompt_text(
        self,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]],
        language: str,
        top_redflag_questions: Optional[List[Tuple[str, float, str]]],
    ) -> str:
        """Get the full prompt text that will be sent to LLM (for logging purposes)."""
        # Recreate the prompt using the same logic as the adapter
        from src.utils.redflag_utils import format_redflag_questions_for_llm, format_violated_filter_questions_for_llm
        
        score_percentage = round(toxic_score * 100, 1)
        avg_score_percentage = round(avg_toxic_score * 100, 1)
        
        # Calculate relative toxicity
        relative_toxicity = "higher" if toxic_score > avg_toxic_score else "lower" if toxic_score < avg_toxic_score else "similar"
        relative_diff = abs(toxic_score - avg_toxic_score) * 100
        
        redflag_section = ""
        if top_redflag_questions:
            redflag_section = "\n\n" + format_redflag_questions_for_llm(top_redflag_questions, language)
        
        filter_section = ""
        if violated_filter_questions:
            filter_section = "\n\n" + format_violated_filter_questions_for_llm(violated_filter_questions, language)
        
        # System message (used by Groq)
        system_msg = "You are a supportive relationship counselor providing empathetic insights based on survey results."
        
        # User prompt
        if language == "TR":
            user_prompt = f"""Bir ilişki toksisite anketine dayanarak, {user_name} için partneri {bf_name} hakkında kısa, destekleyici içgörüler sağlayın.

Anket Sonuçları:
- Toksisite Skoru: %{score_percentage} (%0 = toksik değil, %100 = çok toksik)
- Ortalama Toksisite Skoru (tüm kullanıcılar): %{avg_score_percentage}
- Göreceli Toksisite: Ortalamadan {relative_toxicity} (%{relative_diff:.1f} fark)
- Filtre İhlalleri: {bf_name} {filter_violations} güvenlik filtresini geçemedi{filter_section}{redflag_section}

Lütfen şunları sağlayın:
1. Bu sonuçların ne gösterebileceğine dair detaylı bir analiz (daha uzun bölüm - buraya odaklan)
2. Kısa destekleyici tavsiye ve teşvik birleşik (kısa bölüm - 1-2 cümle)

ÖNEMLİ: Yanıtınız kesinlikle 100 kelimeden az olmalı. Maksimum 100 kelime. Kelimelerin çoğunu analiz bölümüne ayırın. Yargılayıcı olmaktan çok destekleyici olmaya odaklanın."""
        else:
            user_prompt = f"""Based on a relationship toxicity survey, provide brief, supportive insights for {user_name} about their partner {bf_name}.

Survey Results:
- Toxicity Score: {score_percentage}% (0% = not toxic, 100% = very toxic)
- Average Toxicity Score (all users): {avg_score_percentage}%
- Relative Toxicity: {relative_toxicity} than average ({relative_diff:.1f}% difference)
- Filter Violations: {bf_name} failed {filter_violations} safety filter(s){filter_section}{redflag_section}

Please provide:
1. A detailed analysis of what these results might indicate (longer section - focus here)
2. Brief supportive advice and encouragement combined (short section - 1-2 sentences)

IMPORTANT: Your response must be strictly under 100 words. Maximum 100 words. Allocate most words to the analysis section. Focus on being supportive rather than judgmental."""
        
        # Return full prompt including system message
        return f"System: {system_msg}\n\nUser: {user_prompt}"

    def close(self):
        """Close the LLM connection."""
        if self.llm and hasattr(self.llm, 'close'):
            self.llm.close()

