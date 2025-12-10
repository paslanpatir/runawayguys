"""Hugging Face Inference API adapter for LLM."""
from typing import Optional, List, Tuple
from src.ports.llm_port import LLMPort
from src.services.insight_prompt_builder import InsightPromptBuilder

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
        self.provider = "huggingface"
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
            
            # For text_generation, combine system and user prompt
            full_prompt = f"{system_msg}\n\n{user_prompt}"

            # Try text_generation first (for most models like flan-t5)
            # Then fallback to chat_completion for conversational models
            try:
                result = self.client.text_generation(
                    full_prompt,
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
                    messages = [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_prompt}
                    ]
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

