"""Main entry point for the Runaway Guys Streamlit app."""
import streamlit as st
from src.main import main

# Configure page
st.set_page_config(
    page_title="RedFlag - Toxic Guy Detector",
    page_icon="🚩",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Database access flags
# Set to False for local testing (uses CSV files)
# Set to True if you have AWS credentials configured
DB_READ = True  # Read from DynamoDB (requires AWS credentials in config/aws_credentials.txt)
DB_WRITE = True  # Write to DynamoDB (requires AWS credentials in config/aws_credentials.txt)

# LLM feature flag
# Set to False to disable AI insights generation
# Set to True if you have LLM API credentials configured (Hugging Face or Groq)
LLM_ENABLED = True  # Enable LLM features (requires HF_API_TOKEN or config/llm_credentials.txt)

# DEBUG MODE: Set to True to skip survey steps and go directly to results page with mock data
# Or add ?debug=true to the URL
DEBUG_MODE = False  # Set to False for normal flow, True for testing with mock data

if __name__ == "__main__":
    import os
    if DEBUG_MODE:
        os.environ["DEBUG_MODE"] = "true"
    main(DB_READ, DB_WRITE, LLM_ENABLED)

