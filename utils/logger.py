import streamlit as st
from datetime import datetime

def init_logs():
    if "agent_logs" not in st.session_state:
        st.session_state.agent_logs = []

def log(agent: str, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.agent_logs.append({
        "time": timestamp,
        "agent": agent,
        "message": message
    })
