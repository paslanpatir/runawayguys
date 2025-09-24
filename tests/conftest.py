# tests/conftest.py
import os
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app_test():
    """Fixture that returns a ready-to-run AppTest for the mini app."""
    # Clean slate session state
    st.session_state.clear()
    st.session_state.user_details = {}

    # Path to your mini app
    script_path = os.path.join(os.path.dirname(__file__), "_mini_app.py")

    # Return AppTest instance (but don't run yet)
    return AppTest(script_path, default_timeout=2)
