# Redflag Questions in AI Insights - Configuration

## Overview

The AI insights feature now includes the top-rated redflag questions and their ratings to provide more context-aware insights.

## Configuration

In `src/application/steps/results_step.py`, you can configure:

```python
TOP_REDFLAG_QUESTIONS_COUNT = 5  # Number of top-rated redflag questions to include
MIN_REDFLAG_RATING = 5.0  # Minimum rating (0-10) to include a question
```

### Parameters

- **`TOP_REDFLAG_QUESTIONS_COUNT`**: 
  - Default: `5`
  - Description: Number of top-rated redflag questions to include in the LLM prompt
  - Range: 1-20 (recommended: 3-10)
  - Higher values provide more context but may increase prompt size and cost

- **`MIN_REDFLAG_RATING`**:
  - Default: `5.0`
  - Description: Minimum rating threshold (0-10 scale) to include a question
  - Range: 0.0-10.0
  - Only questions with ratings >= this value will be included
  - Recommended: 5.0-7.0 to focus on concerning behaviors

## How It Works

1. **Question Selection**: The system selects the top N redflag questions based on:
   - Rating value (highest first)
   - Minimum rating threshold
   - Excludes "not applicable" questions (NaN values)

2. **Formatting**: Selected questions are formatted as:
   - English: "Top-rated red flag questions: 1. Question text (Rating: 8.5/10)"
   - Turkish: "En yüksek puanlı kırmızı bayrak soruları: 1. Soru metni (Puan: 8.5/10)"

3. **LLM Integration**: The formatted questions are included in the LLM prompt, allowing the AI to:
   - Reference specific concerning behaviors
   - Provide more targeted advice
   - Give context-aware insights

## Example

If a user rates these questions highly:
- "Does he control who you see?" → 9/10
- "Does he check your phone?" → 8/10
- "Does he get angry when you disagree?" → 7/10

The LLM will receive:
```
Top-rated red flag questions:
1. Does he control who you see? (Rating: 9.0/10)
2. Does he check your phone? (Rating: 8.0/10)
3. Does he get angry when you disagree? (Rating: 7.0/10)
```

This allows the AI to provide insights like:
> "Based on your responses, controlling behaviors (rating 9/10) and privacy violations (rating 8/10) are significant concerns. These patterns suggest..."

## Customization

### To include more questions:
```python
TOP_REDFLAG_QUESTIONS_COUNT = 10
MIN_REDFLAG_RATING = 4.0  # Lower threshold to include more questions
```

### To focus on only very concerning behaviors:
```python
TOP_REDFLAG_QUESTIONS_COUNT = 3
MIN_REDFLAG_RATING = 7.0  # Only include questions rated 7 or higher
```

### To include all questions above a threshold:
```python
TOP_REDFLAG_QUESTIONS_COUNT = 50  # Large number to include all
MIN_REDFLAG_RATING = 5.0
```

## Function Reference

The utility function `get_top_redflag_questions()` is located in `src/utils/redflag_utils.py`:

```python
def get_top_redflag_questions(
    redflag_responses: Dict[str, float],
    questions: List[RedFlagQuestion],
    language: str = "EN",
    top_n: int = 5,
    min_rating: float = 0.0,
) -> List[Tuple[str, float, str]]:
    """
    Get top N redflag questions with highest ratings.
    
    Returns:
        List of tuples: (question_text, rating, question_id)
        Sorted by rating (highest first), limited to top_n
    """
```

## Notes

- Questions with NaN values (marked as "not applicable") are automatically excluded
- Questions are sorted by rating in descending order
- If fewer questions meet the criteria than `TOP_REDFLAG_QUESTIONS_COUNT`, only available questions are included
- The function gracefully handles missing questions or invalid data

