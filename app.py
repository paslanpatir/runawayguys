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
DB_READ = False  # Read from CSV files locally
DB_WRITE = False  # Write to CSV files locally

if __name__ == "__main__":
    main(DB_READ, DB_WRITE)

