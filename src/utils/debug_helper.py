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
            "bf_name": "test",
        }
    
    # Set mock survey results - toxic_score will be calculated from actual responses
    st.session_state.filter_violations = 2  # 2 safety filter violations
    
    # Set mock redflag responses (with some high ratings for insights)
    st.session_state.redflag_responses = {
        "Q1": 8.5,  # High rating - will appear in insights
        "Q2": 7.0,  # High rating
        "Q3": 6.5,  # High rating
        "Q4": 5.0,  # Medium rating
        "Q5": 3.0,  # Low rating
        "Q6": 2.0,  # Low rating
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
        
        # Load redflag questions
        actual_questions = repository.get_redflag_questions()
        
        if actual_questions:
            # Randomize the questions (same as real flow)
            questions = random.sample(actual_questions, len(actual_questions))
            st.session_state.randomized_questions = questions
            
            # Update redflag_responses to match actual question IDs
            # Create realistic responses: mix of high, medium, and low ratings
            # This simulates a real scenario where some behaviors are concerning
            actual_responses = {}
            num_questions_to_answer = min(15, len(questions))  # Answer more questions for realism
            
            # Calculate toxic_score from responses (same formula as redflag_questions_step.py)
            tot_score = 0
            abs_tot_score = 0
            applicable_questions = 0
            yes_no_default_score = 7
            
            for i, question in enumerate(questions[:num_questions_to_answer]):
                q_id = question.question_id
                scoring_type = question.scoring
                weight = question.weight
                
                # Create a realistic distribution:
                # - First 20%: High concern (7.5-9.0) - major red flags
                # - Next 30%: Medium-high concern (5.0-7.0) - concerning behaviors
                # - Next 30%: Low-medium concern (2.0-4.5) - minor issues
                # - Last 20%: Low concern (0.5-1.5) - mostly okay
                
                if i < num_questions_to_answer * 0.2:
                    # High concern - major red flags
                    rating = 7.5 + (i * 0.3)  # 7.5-9.0 range
                elif i < num_questions_to_answer * 0.5:
                    # Medium-high concern
                    rating = 5.0 + ((i - num_questions_to_answer * 0.2) * 0.15)  # 5.0-7.0 range
                elif i < num_questions_to_answer * 0.8:
                    # Low-medium concern
                    rating = 2.0 + ((i - num_questions_to_answer * 0.5) * 0.08)  # 2.0-4.5 range
                else:
                    # Low concern - mostly okay
                    rating = 0.5 + ((i - num_questions_to_answer * 0.8) * 0.05)  # 0.5-1.5 range
                
                # For YES/NO questions, convert to binary (7 or 0)
                if scoring_type == "YES/NO":
                    rating = yes_no_default_score if rating >= 3.5 else 0
                
                # Round to 1 decimal place for Range(0-10) questions, integer for YES/NO
                if scoring_type == "Range(0-10)":
                    rating = round(rating, 1)
                else:
                    rating = int(rating)
                
                actual_responses[f"Q{q_id}"] = rating
                
                # Calculate toxic_score components (same as redflag_questions_step.py)
                tot_score += weight * rating
                max_score = yes_no_default_score if scoring_type == "YES/NO" else 10
                abs_tot_score += weight * max_score * (1 if weight > 0 else -1)
                applicable_questions += 1
            
            # Calculate toxic_score from responses
            if applicable_questions > 0:
                toxic_score = Decimal("1.0") * Decimal(str(tot_score)) / Decimal(str(abs_tot_score))
                toxic_score_float = float(toxic_score)
            else:
                toxic_score_float = 0.0
            
            st.session_state.redflag_responses = actual_responses
            st.session_state.toxic_score = toxic_score_float
            print(f"[DEBUG] Loaded {len(questions)} actual redflag questions from database")
            print(f"[DEBUG] Created responses for {len(actual_responses)} redflag questions")
            print(f"[DEBUG] Calculated toxic_score: {toxic_score_float:.4f} from {applicable_questions} applicable questions")
        else:
            print("[WARNING] No redflag questions found in database. Using mock questions.")
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
        
        # Load filter questions and create responses that actually violate some filters
        filter_questions = repository.get_filter_questions()
        
        if filter_questions:
            # Randomize filter questions (same as real flow)
            randomized_filters = random.sample(filter_questions, len(filter_questions))
            st.session_state.randomized_filters = randomized_filters
            
            # Create realistic filter responses that match actual question IDs
            # Make sure 2 filters are violated (answer >= upper_limit) for realism
            filter_responses = {}
            violations = 0
            violation_count = 0
            target_violations = 2  # Realistic: 2 safety filter violations
            
            for i, question in enumerate(randomized_filters):
                f_id = question.filter_id
                upper_limit = question.upper_limit
                
                # Create violations for first target_violations questions
                if violation_count < target_violations:
                    # Set answer to upper_limit to create a violation
                    answer = upper_limit
                    violations += 1
                    violation_count += 1
                else:
                    # Set answer below upper_limit (no violation) - realistic safe responses
                    # For YES/NO questions (upper_limit=1), set to 0 (No)
                    # For Limit questions, set to a safe value below upper_limit
                    if question.scoring == "YES/NO":
                        answer = 0  # Safe: No
                    else:
                        answer = max(0, upper_limit - 1)  # Safe: below limit
                
                filter_responses[f"F{f_id}"] = answer
            
            st.session_state.filter_responses = filter_responses
            st.session_state.filter_violations = violations
            print(f"[DEBUG] Loaded {len(randomized_filters)} actual filter questions from database")
            print(f"[DEBUG] Created {violations} filter violations out of {len(filter_responses)} responses")
        else:
            print("[WARNING] No filter questions found in database. Using mock filter responses.")
            # Fallback to mock if database is empty
            st.session_state.filter_responses = {
                "F1": 1,
                "F2": 1,
            }
            st.session_state.filter_violations = 2
            
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
        st.session_state.filter_responses = {
            "F1": 1,
            "F2": 1,
        }
        st.session_state.filter_violations = 2
    
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

