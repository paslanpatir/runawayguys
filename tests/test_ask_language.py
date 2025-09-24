import os
from streamlit.testing.v1 import AppTest

def test_language_selection(app_test):
    os.environ["STEP"] = "AskLanguage"  # 👈 choose step

    script_path = os.path.join(os.path.dirname(__file__), "_mini_app.py")
    at = AppTest(script_path, default_timeout=2).run()

    all_texts = [m.value for m in at.markdown]
    assert any("Please select your preferred language" in t for t in all_texts)

    at.radio[0].set_value("EN")
    at.button[0].click().run()

    assert at.session_state["user_details"]["language"] == "EN"
