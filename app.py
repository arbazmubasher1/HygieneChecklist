# app.py
import streamlit as st
from login_page import render_login
from checklist_page import render_checklist

st.set_page_config(page_title="Hygiene Checklist", layout="wide")

# Initialize auth keys once
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# Simple router
page = st.session_state.get("page")
if not st.session_state["authenticated"]:
    st.session_state["page"] = "login"
    render_login()
else:
    st.session_state["page"] = "checklist"
    render_checklist()
