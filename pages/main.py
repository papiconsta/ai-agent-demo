"""
    This is like a react app Main.tsx file in which has the pages as routers
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

st.set_page_config(page_title="AI Demo", page_icon="🤖", layout="centered")

# the session ofcourse is set on False, you need to login first.
st.session_state.setdefault("logged_in", False)

if st.session_state.logged_in:
    pages = [
        st.Page("home.py", title="Home", icon=":material/home:"),
        # st.Page("evaluations.py", title="Evaluations", icon=":material/fact_check:"),
        st.Page("monitor.py", title="Monitor", icon=":material/monitoring:"),
        st.Page("settings.py", title="Settings", icon=":material/settings:"),
    ]
else:
    pages = [
        st.Page("login.py", title="Login", icon=":material/login:"),
        st.Page("signup.py", title="Sign up", icon=":material/person_add:"),
    ]

page = st.navigation(pages)
page.run()
