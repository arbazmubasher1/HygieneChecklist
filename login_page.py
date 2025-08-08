# login_page.py
import streamlit as st
import time

def render_login():
    st.title("🔐 Login to Access Hygiene Checklist")

    valid_users = {
        f"person@{b.lower().replace(' ', '').replace('-', '')}.com": "123"
        for b in ["DHA-P6", "DHA-CC", "Cloud Kitchen", "Johar Town", "Bahria", "Wehshi Lab", "Emporium"]
    }

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Login", key="login_button"):
            if email and email.lower() in valid_users and password == valid_users[email.lower()]:
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = email
                # Force a clean rerun into the checklist page
                st.session_state["page"] = "checklist"
                st.rerun()
            else:
                st.error("Invalid email or password.")
    with col2:
        # Optional: clear just in case user wants to reset the login form
        if st.button("Clear", key="clear_login"):
            for k in ("login_email", "login_password"):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
