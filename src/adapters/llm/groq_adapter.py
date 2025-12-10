"""Groq API adapter for LLM."""
from typing import Optional, List, Tuple
from src.ports.llm_port import LLMPort
from src.utils.redflag_utils import format_redflag_questions_for_llm, format_violated_filter_questions_for_llm

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
            # Create prompt based on language
            if language == "TR":
                prompt = self._create_turkish_prompt(
                    user_name, bf_name, toxic_score, avg_toxic_score, 
                    filter_violations, violated_filter_questions, top_redflag_questions
                )
            else:
                prompt = self._create_english_prompt(
                    user_name, bf_name, toxic_score, avg_toxic_score,
                    filter_violations, violated_filter_questions, top_redflag_questions
                )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a supportive relationship counselor providing empathetic insights based on survey results."
                    },
                    {
                        "role": "user",
                        "content": prompt
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

    def _create_english_prompt(
        self,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
    ) -> str:
        """Create English prompt for insights generation."""
        score_percentage = round(toxic_score * 100, 1)
        avg_score_percentage = round(avg_toxic_score * 100, 1)
        
        # Calculate relative toxicity
        relative_toxicity = "higher" if toxic_score > avg_toxic_score else "lower" if toxic_score < avg_toxic_score else "similar"
        relative_diff = abs(toxic_score - avg_toxic_score) * 100
        
        # Format redflag questions if provided
        redflag_section = ""
        if top_redflag_questions:
            redflag_section = "\n\n" + format_redflag_questions_for_llm(top_redflag_questions, "EN")
        
        # Format violated filter questions if provided
        filter_section = ""
        if violated_filter_questions:
            filter_section = "\n\n" + format_violated_filter_questions_for_llm(violated_filter_questions, "EN")
        
        return f"""Based on a relationship toxicity survey, provide brief, supportive insights for {user_name} about their partner {bf_name}.

Survey Results:
- Toxicity Score: {score_percentage}% (0% = not toxic, 100% = very toxic)
- Average Toxicity Score (all users): {avg_score_percentage}%
- Relative Toxicity: {relative_toxicity} than average ({relative_diff:.1f}% difference)
- Filter Violations: {bf_name} failed {filter_violations} safety filter(s){filter_section}{redflag_section}

Please provide:
1. A detailed analysis of what these results might indicate (longer section - focus here)
2. Brief supportive advice and encouragement combined (short section - 1-2 sentences)

IMPORTANT: Your response must be strictly under 100 words. Maximum 100 words. Allocate most words to the analysis section. Focus on being supportive rather than judgmental."""

    def _create_turkish_prompt(
        self,
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
    ) -> str:
        """Create Turkish prompt for insights generation."""
        score_percentage = round(toxic_score * 100, 1)
        avg_score_percentage = round(avg_toxic_score * 100, 1)
        
        # Calculate relative toxicity
        relative_toxicity = "daha yüksek" if toxic_score > avg_toxic_score else "daha düşük" if toxic_score < avg_toxic_score else "benzer"
        relative_diff = abs(toxic_score - avg_toxic_score) * 100
        
        # Format redflag questions if provided
        redflag_section = ""
        if top_redflag_questions:
            redflag_section = "\n\n" + format_redflag_questions_for_llm(top_redflag_questions, "TR")
        
        # Format violated filter questions if provided
        filter_section = ""
        if violated_filter_questions:
            filter_section = "\n\n" + format_violated_filter_questions_for_llm(violated_filter_questions, "TR")
        
        return f"""Bir ilişki toksisite anketine dayanarak, {user_name} için partneri {bf_name} hakkında kısa, destekleyici içgörüler sağlayın.

Anket Sonuçları:
- Toksisite Skoru: %{score_percentage} (%0 = toksik değil, %100 = çok toksik)
- Ortalama Toksisite Skoru (tüm kullanıcılar): %{avg_score_percentage}
- Göreceli Toksisite: Ortalamadan {relative_toxicity} (%{relative_diff:.1f} fark)
- Filtre İhlalleri: {bf_name} {filter_violations} güvenlik filtresini geçemedi{filter_section}{redflag_section}

Lütfen şunları sağlayın:
1. Bu sonuçların ne gösterebileceğine dair detaylı bir analiz (daha uzun bölüm - buraya odaklan)
2. Kısa destekleyici tavsiye ve teşvik birleşik (kısa bölüm - 1-2 cümle)

ÖNEMLİ: Yanıtınız kesinlikle 100 kelimeden az olmalı. Maksimum 100 kelime. Kelimelerin çoğunu analiz bölümüne ayırın. Yargılayıcı olmaktan çok destekleyici olmaya odaklanın."""

