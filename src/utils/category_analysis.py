"""Utility functions for category-based toxicity analysis."""
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
import numpy as np
from src.domain.value_objects import RedFlagQuestion


def calculate_category_toxicity_scores(
    redflag_responses: Dict[str, float],
    questions: List[RedFlagQuestion],
    language: str = "EN",
    category_names_map: Optional[Dict[int, str]] = None,
) -> Dict[str, Tuple[float, int]]:
    """
    Calculate average toxicity score per category.
    
    Args:
        redflag_responses: Dictionary mapping question_id (e.g., "Q1") to rating (0-10)
        questions: List of RedFlagQuestion objects
        language: Language code (TR or EN) - used for category name lookup
        category_names_map: Optional dictionary mapping category_id to category_name (language-specific)
        
    Returns:
        Dictionary mapping category_name to (average_score, question_count)
        Categories with no responses are excluded.
    """
    # Create mapping from question_id to question object
    question_map = {f"Q{q.question_id}": q for q in questions}
    
    # Debug: Check question categories (ASCII-safe)
    categories_found = set()
    questions_without_category = 0
    for q in questions[:10]:  # Check first 10 questions
        if q.category_name:
            categories_found.add(q.category_name)
        else:
            questions_without_category += 1
    # Print only count to avoid Unicode issues on Windows
    print(f"[DEBUG] Sample categories found in questions: {len(categories_found)} categories")
    print(f"[DEBUG] Questions without category (first 10): {questions_without_category}")
    
    # Group responses by category with weights
    category_weighted_scores: Dict[str, List[Tuple[float, float]]] = {}  # (rating, weight)
    category_counts: Dict[str, int] = {}
    responses_without_category = 0
    
    for q_id, rating in redflag_responses.items():
        # Skip NaN or None values
        if rating is None or (isinstance(rating, float) and (rating != rating)):  # NaN check
            continue
        
        # Convert to float if Decimal
        if isinstance(rating, Decimal):
            rating = float(rating)
        
        # Get question object
        question = question_map.get(q_id)
        if question:
            # Use category_names_map if provided (for language-specific names)
            # Otherwise fall back to question.category_name
            if category_names_map and question.category_id:
                category = category_names_map.get(question.category_id)
            elif question.category_name:
                category = question.category_name
            else:
                category = None
            
            if category:
                if category not in category_weighted_scores:
                    category_weighted_scores[category] = []
                    category_counts[category] = 0
                # Store rating and weight together
                weight = float(question.weight) if question.weight else 1.0
                category_weighted_scores[category].append((rating, weight))
                category_counts[category] += 1
            else:
                responses_without_category += 1
        else:
            print(f"[DEBUG] Question not found for {q_id}")
    
    print(f"[DEBUG] Responses without category: {responses_without_category}")
    # Print only count to avoid Unicode issues on Windows
    print(f"[DEBUG] Categories with scores: {len(category_weighted_scores)} categories")
    
    # Calculate weighted averages
    result = {}
    for category, weighted_scores in category_weighted_scores.items():
        if weighted_scores:  # Only include categories with at least one response
            # Calculate weighted average: sum(rating * weight) / sum(weight)
            total_weighted_score = sum(rating * weight for rating, weight in weighted_scores)
            total_weight = sum(weight for _, weight in weighted_scores)
            if total_weight > 0:
                avg_score = total_weighted_score / total_weight
            else:
                avg_score = sum(rating for rating, _ in weighted_scores) / len(weighted_scores)  # Fallback to simple average
            result[category] = (avg_score, category_counts[category])
    
    return result


def normalize_category_scores(
    category_scores: Dict[str, Tuple[float, int]],
    max_score: float = 10.0,
) -> Dict[str, float]:
    """
    Normalize category scores to 0-1 range for radar chart.
    
    Args:
        category_scores: Dictionary mapping category_name to (average_score, count)
        max_score: Maximum possible score (default: 10.0)
        
    Returns:
        Dictionary mapping category_name to normalized score (0-1)
    """
    return {
        category: score / max_score
        for category, (score, count) in category_scores.items()
    }

