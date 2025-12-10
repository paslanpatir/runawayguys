"""Hugging Face Inference API adapter for LLM."""
from typing import Optional, List, Tuple
from src.ports.llm_port import LLMPort
from src.utils.redflag_utils import format_redflag_questions_for_llm, format_violated_filter_questions_for_llm

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None  # huggingface_hub package not installed


class HuggingFaceAdapter(LLMPort):
    """Hugging Face Inference API implementation of LLMPort."""

    def __init__(self, api_key: str, model_name: str = "gpt2"):
        if InferenceClient is None:
            raise ImportError("huggingface_hub package is not installed. Install it with: pip install huggingface_hub")
        
        self.api_key = api_key
        self.model_name = model_name
        # Use InferenceClient with 'hf-inference' provider (Hugging Face's own inference service)
        # This is the most reliable option for free tier
        try:
            self.client = InferenceClient(
                model=model_name,
                token=api_key,
                provider="hf-inference"  # Use Hugging Face's own inference service
            )
        except Exception as e:
            # Fallback to auto if hf-inference fails
            print(f"[WARNING] hf-inference provider failed, trying auto: {e}")
            self.client = InferenceClient(
                model=model_name,
                token=api_key,
                provider="auto"  # Auto-select from available providers
            )

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
        Generate insights using Hugging Face Inference API.
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

            # Try text_generation first (for most models like flan-t5)
            # Then fallback to chat_completion for conversational models
            try:
                result = self.client.text_generation(
                    prompt,
                    max_new_tokens=300,
                    temperature=0.7,
                    return_full_text=False,
                )
                if result:
                    return result.strip()
            except Exception as text_error:
                # Fallback to chat_completion if text_generation fails (for conversational models)
                print(f"[INFO] text_generation failed, trying chat_completion: {text_error}")
                try:
                    messages = [{"role": "user", "content": prompt}]
                    response = self.client.chat_completion(
                        messages=messages,
                        max_tokens=300,
                        temperature=0.7,
                    )
                    
                    # Extract the response text from chat completion
                    if response:
                        if hasattr(response, 'choices') and len(response.choices) > 0:
                            return response.choices[0].message.content.strip()
                        elif isinstance(response, dict):
                            if 'choices' in response and len(response['choices']) > 0:
                                return response['choices'][0]['message']['content'].strip()
                            elif 'generated_text' in response:
                                return response['generated_text'].strip()
                        elif isinstance(response, str):
                            return response.strip()
                except Exception as chat_error:
                    print(f"[ERROR] Both text_generation and chat_completion failed: {chat_error}")
                    raise text_error  # Raise the original error
            
            return None

        except Exception as e:
            print(f"[ERROR] Hugging Face API error: {e}")
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
1. A brief analysis of what these results might indicate
2. Supportive advice (2-3 sentences)
3. Encouragement to prioritize their well-being

Keep the response concise, empathetic, and under 200 words. Focus on being supportive rather than judgmental."""

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
1. Bu sonuçların ne gösterebileceğine dair kısa bir analiz
2. Destekleyici tavsiye (2-3 cümle)
3. Kendi refahını önceliklendirmesi için teşvik

Yanıtı kısa, empatik ve 200 kelimeden az tutun. Yargılayıcı olmaktan çok destekleyici olmaya odaklanın."""

