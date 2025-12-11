"""Utility functions for redflag questions and responses."""
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
from src.domain.value_objects import RedFlagQuestion, FilterQuestion


def get_top_redflag_questions(
    redflag_responses: Dict[str, float],
    questions: List[RedFlagQuestion],
    language: str = "EN",
    top_n: int = 5,
    min_rating: float = 0.0,
    use_english_for_llm: bool = False,
) -> List[Tuple[str, float, str]]:
    """
    Get top N redflag questions with highest ratings.
    
    Args:
        redflag_responses: Dictionary mapping question_id (e.g., "Q1") to rating (0-10)
        questions: List of RedFlagQuestion objects
        language: Language code (TR or EN) - used for display
        top_n: Number of top questions to return (default: 5)
        min_rating: Minimum rating threshold to include (default: 0.0)
        use_english_for_llm: If True, always return English question texts (for LLM prompts)
        
    Returns:
        List of tuples: (question_text, rating, question_id)
        Sorted by rating (highest first), limited to top_n
    """
    # Create a mapping from question_id to question object
    question_map = {f"Q{q.question_id}": q for q in questions}
    
    # Filter and collect questions with ratings
    rated_questions = []
    for q_id, rating in redflag_responses.items():
        # Skip NaN or None values
        if rating is None or (isinstance(rating, float) and (rating != rating)):  # NaN check
            continue
        
        # Convert to float if Decimal
        if isinstance(rating, Decimal):
            rating = float(rating)
        
        # Skip if below minimum rating
        if rating < min_rating:
            continue
        
        # Get question object
        question = question_map.get(q_id)
        if question:
            # Use English for LLM, otherwise use specified language
            question_lang = "EN" if use_english_for_llm else language
            question_text = question.get_question(question_lang)
            rated_questions.append((question_text, rating, q_id))
    
    # Sort by rating (highest first)
    rated_questions.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N
    return rated_questions[:top_n]


def format_redflag_questions_for_llm(
    top_questions: List[Tuple[str, float, str]],
    language: str = "EN",
) -> str:
    """
    Format redflag questions for LLM prompt.
    
    Args:
        top_questions: List of tuples (question_text, rating, question_id)
        language: Language code (TR or EN)
        
    Returns:
        Formatted string for LLM prompt
    """
    if not top_questions:
        return ""
    
    if language == "TR":
        lines = ["En yüksek puanlı kırmızı bayrak soruları:"]
        for i, (question_text, rating, q_id) in enumerate(top_questions, 1):
            lines.append(f"{i}. {question_text} (Puan: {rating:.1f}/10)")
    else:
        lines = ["Top-rated red flag questions:"]
        for i, (question_text, rating, q_id) in enumerate(top_questions, 1):
            lines.append(f"{i}. {question_text} (Rating: {rating:.1f}/10)")
    
    return "\n".join(lines)


def get_violated_filter_questions(
    filter_responses: Dict[str, int],
    questions: List[FilterQuestion],
    language: str = "EN",
    use_english_for_llm: bool = False,
) -> List[Tuple[str, int, str]]:
    """
    Get filter questions that were violated (answer >= upper_limit).
    
    Args:
        filter_responses: Dictionary mapping filter_id (e.g., "F1") to answer (0 or 1 for YES/NO, or score for Limit)
        questions: List of FilterQuestion objects
        language: Language code (TR or EN) - used for display
        use_english_for_llm: If True, always return English question texts (for LLM prompts)
        
    Returns:
        List of tuples: (question_text, answer, filter_id)
        Only includes questions where answer >= upper_limit
    """
    # Create a mapping from filter_id to question object
    question_map = {f"F{q.filter_id}": q for q in questions}
    
    if not questions:
        return []
    
    # Filter and collect violated questions
    violated_questions = []
    for f_id, answer in filter_responses.items():
        # Get question object
        question = question_map.get(f_id)
        if question:
            if answer >= question.upper_limit:
                # Use English for LLM, otherwise use specified language
                question_lang = "EN" if use_english_for_llm else language
                question_text = question.get_question(question_lang)
                violated_questions.append((question_text, answer, f_id))
    
    return violated_questions


def format_violated_filter_questions_for_llm(
    violated_questions: List[Tuple[str, int, str]],
    language: str = "EN",
) -> str:
    """
    Format violated filter questions for LLM prompt.
    
    Args:
        violated_questions: List of tuples (question_text, answer, filter_id)
        language: Language code (TR or EN)
        
    Returns:
        Formatted string for LLM prompt
    """
    if not violated_questions:
        return ""
    
    if language == "TR":
        lines = ["İhlal edilen güvenlik filtreleri:"]
        for i, (question_text, answer, f_id) in enumerate(violated_questions, 1):
            lines.append(f"{i}. {question_text}")
    else:
        lines = ["Violated safety filters:"]
        for i, (question_text, answer, f_id) in enumerate(violated_questions, 1):
            lines.append(f"{i}. {question_text}")
    
    return "\n".join(lines)

