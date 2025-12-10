"""Prompt builder for LLM insights generation."""
from typing import Optional, List, Tuple
from src.utils.redflag_utils import format_redflag_questions_for_llm, format_violated_filter_questions_for_llm


class InsightPromptBuilder:
    """Builder class for creating prompts for LLM insights generation."""
    
    # System message (used by Groq and other chat-based models)
    SYSTEM_MESSAGE_EN = "You are a supportive relationship counselor providing empathetic insights based on survey results."
    SYSTEM_MESSAGE_TR = "Anket sonuçlarına dayalı empatik içgörüler sağlayan destekleyici bir ilişki danışmanısınız."
    
    @staticmethod
    def build_prompt(
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
        language: str = "EN",
        max_words: int = 100,
    ) -> Tuple[str, str]:
        """
        Build the full prompt for LLM insights generation.
        
        Args:
            user_name: Name of the user
            bf_name: Boyfriend's name
            toxic_score: Toxicity score (0-1)
            avg_toxic_score: Average toxicity score from all users (0-1)
            filter_violations: Number of filter violations
            violated_filter_questions: List of violated filter questions
            top_redflag_questions: List of top redflag questions with ratings
            language: Language code (TR or EN)
            max_words: Maximum number of words for the response (default: 100)
            
        Returns:
            Tuple of (system_message, user_prompt)
        """
        if language == "TR":
            system_msg = InsightPromptBuilder.SYSTEM_MESSAGE_TR
            user_prompt = InsightPromptBuilder._build_turkish_prompt(
                user_name, bf_name, toxic_score, avg_toxic_score,
                filter_violations, violated_filter_questions, top_redflag_questions, max_words
            )
        else:
            system_msg = InsightPromptBuilder.SYSTEM_MESSAGE_EN
            user_prompt = InsightPromptBuilder._build_english_prompt(
                user_name, bf_name, toxic_score, avg_toxic_score,
                filter_violations, violated_filter_questions, top_redflag_questions, max_words
            )
        
        return system_msg, user_prompt
    
    @staticmethod
    def build_full_prompt_text(
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
        language: str = "EN",
        max_words: int = 100,
    ) -> str:
        """
        Build the full prompt text including system message (for logging purposes).
        
        Args:
            Same as build_prompt
            
        Returns:
            Full prompt text as string (System: ... User: ...)
        """
        system_msg, user_prompt = InsightPromptBuilder.build_prompt(
            user_name, bf_name, toxic_score, avg_toxic_score,
            filter_violations, violated_filter_questions, top_redflag_questions, language, max_words
        )
        return f"System: {system_msg}\n\nUser: {user_prompt}"
    
    @staticmethod
    def _build_english_prompt(
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
        max_words: int = 100,
    ) -> str:
        """Build English prompt for insights generation."""
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
3. A harsh reality, exactly one sentence, in a tone like deadpan, blunt, low-energy, mildly sarcastic, emotionally detached, and ruthlessly concise, without crossing into abuse.

IMPORTANT: Your response must be strictly under {max_words} words. Maximum {max_words} words. Allocate most words to the analysis section. Focus on being supportive rather than judgmental."""
    
    @staticmethod
    def _build_turkish_prompt(
        user_name: str,
        bf_name: str,
        toxic_score: float,
        avg_toxic_score: float,
        filter_violations: int,
        violated_filter_questions: Optional[List[Tuple[str, int, str]]] = None,
        top_redflag_questions: Optional[List[Tuple[str, float, str]]] = None,
        max_words: int = 100,
    ) -> str:
        """Build Turkish prompt for insights generation."""
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
3. Sert bir gerçeklik, tam olarak bir cümle, ölü tonlu, doğrudan, düşük enerjili, hafifçe alaycı, duygusal olarak mesafeli ve acımasızca özlü bir tonda, ancak istismara kaçmadan.

ÖNEMLİ: Yanıtınız kesinlikle {max_words} kelimeden az olmalı. Maksimum {max_words} kelime. Kelimelerin çoğunu analiz bölümüne ayırın. Yargılayıcı olmaktan çok destekleyici olmaya odaklanın."""

