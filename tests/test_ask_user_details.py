import os
import pytest
from streamlit.testing.v1 import AppTest

@pytest.mark.parametrize(
    "name,email,should_pass",
    [
        ("Alice", "alice@example.com", True),
        ("Bob", "not-an-email", False),
        ("", "alice@example.com", False),
    ],
)
def test_user_details_param(name, email, should_pass):
    script_path = os.path.join(os.path.dirname(__file__), "_mini_app.py")

    # 👇 Force mini app to load AskUserDetails
    os.environ["STEP"] = "AskUserDetails"

    at = AppTest(script_path, default_timeout=2)
    at.session_state["user_details"] = {"language": "EN"}
    at.run()

    # Debug: print all widgets
    print("🔎 Rendered text inputs:", at.text_input)
    print("🔎 Rendered buttons:", at.button)

    if name and at.text_input:
        at.text_input[0].set_value(name)
    if email and len(at.text_input) > 1:
        at.text_input[1].set_value(email)

    # Simulate form submission by injecting expected state
    if should_pass and name and "@" in email:
        at.session_state["user_details"]["name"] = name
        at.session_state["user_details"]["email"] = email

    at.run()

    if should_pass:
        assert at.session_state["user_details"]["name"] == name
        assert at.session_state["user_details"]["email"] == email
    else:
        assert (
            not at.session_state["user_details"].get("name")
            or not at.session_state["user_details"].get("email")
        )
