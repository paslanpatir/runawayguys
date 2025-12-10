"""Debug helper to populate session state with mock data for testing."""
import streamlit as st
from decimal import Decimal


def setup_mock_data_for_testing():
    """
    Populate session state with mock survey data for testing insights.
    This allows skipping directly to the results page.
    """
    # Set user details
    if "user_details" not in st.session_state:
        st.session_state.user_details = {
            "user_id": "test-user-123",
            "name": "Test User",
            "email": "test@example.com",
            "language": "EN",  # Change to "TR" for Turkish
            "bf_name": "John",
        }
    
    # Set mock survey results
    st.session_state.toxic_score = 0.65  # 65% toxicity
    st.session_state.filter_violations = 2
    
    # Set mock redflag responses (with some high ratings for insights)
    st.session_state.redflag_responses = {
        "Q1": 8.5,  # High rating - will appear in insights
        "Q2": 7.0,  # High rating
        "Q3": 6.5,  # High rating
        "Q4": 5.0,  # Medium rating
        "Q5": 3.0,  # Low rating
        "Q6": 2.0,  # Low rating
    }
    
    # Set mock filter responses
    st.session_state.filter_responses = {
        "F1": 1,
        "F2": 0,
    }
    
    # Set other required states
    st.session_state.survey_completed = False
    st.session_state.submitted = False
    st.session_state.new_survey_opt = False
    st.session_state.report_sent = False
    st.session_state.data_saved = False
    
    # Set current step to results (step index 8 in main.py)
    st.session_state.current_step = 8  # ResultsStep index
    
    # Load actual questions from database instead of mock questions
    # This ensures question IDs match the actual database questions
    try:
        from src.adapters.database.database_handler import DatabaseHandler
        from src.adapters.database.question_repository import QuestionRepository
        import random
        
        db_read_allowed = st.session_state.get("db_read_allowed", False)
        db_handler = DatabaseHandler(db_read_allowed=db_read_allowed)
        repository = QuestionRepository(db_handler)
        actual_questions = repository.get_redflag_questions()
        
        if actual_questions:
            # Randomize the questions (same as real flow)
            questions = random.sample(actual_questions, len(actual_questions))
            st.session_state.randomized_questions = questions
            
            # Update redflag_responses to match actual question IDs
            # Create responses for first 6 questions with high ratings
            actual_responses = {}
            for i, question in enumerate(questions[:6]):
                q_id = question.question_id
                # Set high ratings for first 3, medium for next 2, low for last 1
                if i < 3:
                    rating = 8.5 - (i * 0.5)  # 8.5, 8.0, 7.5
                elif i < 5:
                    rating = 6.0 - ((i - 3) * 0.5)  # 6.0, 5.5
                else:
                    rating = 3.0
                actual_responses[f"Q{q_id}"] = rating
            
            st.session_state.redflag_responses = actual_responses
            print(f"[DEBUG] Loaded {len(questions)} actual questions from database")
            print(f"[DEBUG] Created responses for {len(actual_responses)} questions")
        else:
            print("[WARNING] No questions found in database. Using mock questions.")
            # Fallback to mock if database is empty
            from src.domain.value_objects import RedFlagQuestion
            mock_questions = [
                RedFlagQuestion(
                    question_id=1,
                    question_en="Does he control who you see?",
                    question_tr="Senin kiminle görüştüğünü kontrol ediyor mu?",
                    scoring="Range(0-10)",
                    weight=1.0,
                ),
            ]
            st.session_state.randomized_questions = mock_questions
    except Exception as e:
        print(f"[ERROR] Failed to load questions from database: {e}")
        print("[WARNING] Using mock questions as fallback.")
        # Fallback to minimal mock if database fails
        from src.domain.value_objects import RedFlagQuestion
        mock_questions = [
            RedFlagQuestion(
                question_id=1,
                question_en="Mock question (database unavailable)",
                question_tr="Mock soru (veritabanı mevcut değil)",
                scoring="Range(0-10)",
                weight=1.0,
            ),
        ]
        st.session_state.randomized_questions = mock_questions
    
    print("[DEBUG] Mock data set up for testing. You can now go directly to results page.")


def is_debug_mode() -> bool:
    """Check if debug mode is enabled via environment variable or query param."""
    import os
    # Check environment variable
    if os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes"):
        return True
    # Check query parameter (for Streamlit)
    if hasattr(st, "query_params") and st.query_params.get("debug") == "true":
        return True
    return False

