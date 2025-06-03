import streamlit as st
from utils import *

st.set_page_config(page_title="Feature Requests", layout="centered")
st.title("💡 Submit a Feature Request")

supabase, controller = authenticate()
show_login(controller)

if "user" not in st.session_state:
    st.warning("Please log in to make a feature request.")
    st.stop()

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
