import streamlit as st
from src.base_step import BaseStep
from src.messages import Message


class Goodbye(BaseStep):
    name = "goodbye"

    def run(self):
        name = self.session.user_details.get("name", "User")

        st.markdown(self.msg.get("goodbye_message", name=name))
        st.balloons()
        return True