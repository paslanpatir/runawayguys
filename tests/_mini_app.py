import os
import streamlit as st
import importlib

if "user_details" not in st.session_state:
    st.session_state["user_details"] = {}
    
if "language" not in st.session_state["user_details"]:
    st.session_state["user_details"]["language"] = "EN"  # default for tests

step_name = os.getenv("STEP", "AskLanguage")
st.write(f"🔎 Running step: {step_name}")   # 👈 add this line

try:
    module_name = "runawayguys.src." + "".join(["_" + c.lower() if c.isupper() else c for c in step_name]).lstrip("_")
    module = importlib.import_module(module_name)
    StepClass = getattr(module, step_name)
    StepClass().run()
except Exception as e:
    st.error(f"⚠️ Could not load step '{step_name}': {e}")
