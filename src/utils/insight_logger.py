"""Logger for debugging LLM insights generation."""
import csv
import os
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path


def log_insight_generation(
    user_id: str,
    user_name: str,
    email: Optional[str],
    bf_name: str,
    language: str,
    toxic_score: float,
    avg_toxic_score: float,
    filter_violations: int,
    violated_filter_questions: Optional[List[Tuple[str, int, str]]],
    top_redflag_questions: Optional[List[Tuple[str, float, str]]],
    generated_insight: Optional[str],
    prompt_text: str,
    model_name: Optional[str],
    session_data: Dict[str, Any],
    output_dir: str = "data",
) -> None:
    """
    Log insight generation data to CSV file for debugging.
    
    Args:
        user_id: User ID
        user_name: User name
        email: User email
        bf_name: Boyfriend name
        language: Language code
        toxic_score: Toxicity score
        avg_toxic_score: Average toxicity score
        filter_violations: Number of filter violations
        violated_filter_questions: List of violated filter questions
        top_redflag_questions: List of top redflag questions with ratings
        generated_insight: Generated insight text
        prompt_text: Full prompt sent to LLM
        model_name: Name of the LLM model used
        session_data: Additional session state data
        output_dir: Directory to save CSV file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    csv_file = os.path.join(output_dir, "session_insights.csv")
    file_exists = os.path.exists(csv_file)
    
    # Format redflag questions for CSV
    redflag_questions_text = ""
    redflag_ratings_text = ""
    if top_redflag_questions:
        questions = [q[0] for q in top_redflag_questions]  # Question texts
        ratings = [str(q[1]) for q in top_redflag_questions]  # Ratings
        redflag_questions_text = " | ".join(questions)
        redflag_ratings_text = " | ".join(ratings)
    
    # Format violated filter questions for CSV
    violated_filter_questions_text = ""
    if violated_filter_questions:
        violated_filter_questions_text = " | ".join([q[0] for q in violated_filter_questions])
    
    # Prepare row data
    row_data = {
        "id": session_data.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "name": user_name,
        "email": email or "",
        "boyfriend_name": bf_name,
        "language": language,
        "toxic_score": toxic_score,
        "avg_toxic_score": avg_toxic_score,
        "filter_violations": filter_violations,
        "violated_filter_questions": violated_filter_questions_text,
        "redflag_questions": redflag_questions_text,
        "redflag_ratings": redflag_ratings_text,
        "redflag_questions_count": len(top_redflag_questions) if top_redflag_questions else 0,
        "model_name": model_name or "",
        "prompt_text": prompt_text,
        "generated_insight": generated_insight or "",
        "insight_length": len(generated_insight) if generated_insight else 0,
        # Additional session data
        "filter_responses": str(session_data.get("filter_responses", "")),
        "redflag_responses": str(session_data.get("redflag_responses", "")),
        "toxicity_rating": session_data.get("toxicity_rating", ""),
        "feedback_rating": session_data.get("feedback_rating", ""),
        "session_start_time": session_data.get("session_start_time", ""),
        "result_start_time": session_data.get("result_start_time", ""),
    }
    
    # Write to CSV
    fieldnames = [
        "id", "timestamp", "user_id", "name", "email", "boyfriend_name", "language",
        "toxic_score", "avg_toxic_score", "filter_violations", "violated_filter_questions",
        "redflag_questions", "redflag_ratings", "redflag_questions_count",
        "model_name", "prompt_text", "generated_insight", "insight_length",
        "filter_responses", "redflag_responses",
        "toxicity_rating", "feedback_rating", "session_start_time", "result_start_time",
    ]
    
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_data)
    
    print(f"[DEBUG] Insight generation logged to {csv_file}")

