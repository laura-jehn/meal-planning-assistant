import streamlit as st
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime, timedelta
from supabase import create_client

st.set_page_config(page_title="Feature Requests", layout="centered")
st.title("💡 Submit a Feature Request")

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

controller = CookieController(key='cookies')
access_token = controller.get("access_token")
refresh_token = controller.get("refresh_token")
if refresh_token and access_token and "user" not in st.session_state:
    try:
        user = supabase.auth.get_user(access_token)
    except Exception as e:
        try:
            new_session = supabase.auth.refresh_session(refresh_token).session
            controller.set("access_token", new_session.access_token)
            controller.set("refresh_token", new_session.refresh_token)
            time.sleep(1)
        except Exception as e:
            controller.set("refresh_token", "", expires=datetime.now() + timedelta(days=-1))
            time.sleep(1)
    if user:
        st.session_state.user = user.user

if "user" in st.session_state:
    st.sidebar.write(f"👋 Logged in as: {st.session_state.user.email}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        expires_at = datetime.now() + timedelta(days=-7)
        controller.set("access_token", "", expires=expires_at)
        controller.set("refresh_token", "", expires=expires_at)
        time.sleep(1)
        st.rerun()

if "user" not in st.session_state:
    st.warning("Please log in to make a feature request.")
    st.stop()

################################################# 

st.markdown(
    "Got an idea or something you'd love to see in the app? Let me know below!"
)

with st.form("feature_request_form"):
    comment = st.text_area("Your feature request or feedback", placeholder="What would make your experience better?", height=150)
    name = st.text_input("Your name (optional)", placeholder="Who are you?")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not comment.strip():
            st.warning("Please enter a feature request.")
        else:
            try:
                supabase.table("feature_requests").insert({
                    "comment": comment.strip(),
                    "author": name.strip() if name else None
                }).execute()
            except Exception as e:
                st.error(f"Error submitting feature request: {e}")
                st.stop()
            st.success("✅ Thanks for your feedback!")
