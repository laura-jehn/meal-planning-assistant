import streamlit as st
from supabase import create_client
import time
from datetime import datetime, timedelta
from streamlit_cookies_controller import CookieController

st.set_page_config(page_title="Meal Prep Planner", layout="centered", initial_sidebar_state="expanded")
st.title("🥗 Meal Planning Assistant")

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

controller = CookieController(key='cookies')
cookie_name = "supabase_token"
token = controller.get(cookie_name)
if token and "user" not in st.session_state:
    user = supabase.auth.get_user(token)
    if user:
        st.session_state.user = user.user

#################################################

st.markdown(f"""
Are you also fed up with constantly figuring out what to eat every day, only to realize your partner isn't in the mood for it, or worse — you’re missing half the ingredients?

I definitely am. And with full-time work starting soon, who even has time to plan, shop, and cook every day?

That’s exactly why I built this simple tool to:

- 🗓️ Plan 5 meals a week, ahead of time

- 🛒 Generate one combined grocery list, so you only shop once

- ⭐ Get feedback from your partner, with stars and comments

- 🧠 Save mental energy, and avoid the daily "what do we eat?" dilemma

If you’re also trying to save time and reduce stress around meals, this might be for you too.
""")

def show_login():

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            try:
                result = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = result.user
                token = result.session.access_token
                controller.set(cookie_name, token)
                time.sleep(1)  # wait for cookie to set
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(e)
                st.error("Login failed. Check your email/password.")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Sign Up"):
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Please check your email.")
            except Exception as e:
                st.error("Signup failed. Maybe account already exists?")


if "user" in st.session_state:
    st.sidebar.write(f"👋 Logged in as: {st.session_state.user.email}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        expires_at = datetime.now() + timedelta(days=-7)
        controller.set(cookie_name, "", expires=expires_at)
        time.sleep(1)
        st.rerun()
else:
    show_login()
    st.stop()