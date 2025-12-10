import math
from decimal import Decimal
import re 

def is_valid_email(email):
    """
    Validate the email format using a simple regex.
    """
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None


def safe_decimal(value):
    """Convert numeric values to Decimal, replacing Infinity/NaN with None"""
    if isinstance(value, (int, float)):
        if math.isinf(value) or math.isnan(value):
            return None
        return Decimal(str(value))
    return value

def natural_sort_key(item):
    key = item[0]  # the dictionary key (e.g., "Q1")
    # Extract the number part and convert to integer for proper numerical sorting
    return int(key[1:]) if key[1:].isdigit() else 0

def randomize_questions(data):
    data= data.sample(frac=1).reset_index(drop=True)
    print(f"data is randomized")
    return data


def select_discrete_score_options(language):
    from src.messages import Message
    msg= Message(language)
    opts        = msg.get("limited_opt_answer")
    yes_no_opts = msg.get("boolean_answer")
        
    return opts,yes_no_opts