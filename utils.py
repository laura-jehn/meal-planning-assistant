import streamlit as st
from supabase import create_client
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime, timedelta

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def authenticate():
    supabase = init_connection()
    controller = CookieController(key='cookies')
    access_token = controller.get("access_token")
    refresh_token = controller.get("refresh_token")
    if refresh_token and access_token and "user" not in st.session_state:
        try:
            user = supabase.auth.get_user(access_token)
            st.session_state.user = user.user
        except Exception as e:
            try:
                new_session = supabase.auth.refresh_session(refresh_token).session
                controller.set("access_token", new_session.access_token)
                controller.set("refresh_token", new_session.refresh_token)
                time.sleep(1)
            except Exception as e:
                controller.set("refresh_token", "", expires=datetime.now() + timedelta(days=-1))
                time.sleep(1)

    return supabase, controller

def show_login(controller):
    if "user" in st.session_state:
        st.sidebar.write(f"👋 Logged in as: {st.session_state.user.email}")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            expires_at = datetime.now() + timedelta(days=-7)
            controller.set("access_token", "", expires=expires_at)
            controller.set("refresh_token", "", expires=expires_at)
            time.sleep(1)
            st.rerun()


def get_partner_id(supabase, user_id: str) -> str:
    # Get both directions
    partner = supabase.table("partners").select("partnerA, partnerB").or_(
        f"partnerA.eq.{user_id},partnerB.eq.{user_id}"
    ).execute().data
    
    return partner[0]["partnerB"] if partner[0]["partnerA"] == user_id else partner[0]["partnerA"] if partner else None