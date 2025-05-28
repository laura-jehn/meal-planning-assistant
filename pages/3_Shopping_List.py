import streamlit as st
from groq import Groq
from datetime import date, timedelta, datetime
from streamlit_cookies_controller import CookieController
import time
from supabase import create_client

st.set_page_config(page_title="Shopping List", layout="centered")
st.title("🛒 Shopping List Generator")

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()
groq_client = Groq(
  api_key=st.secrets["GROQ_API_KEY"]
)

controller = CookieController(key='cookies')
access_token = controller.get("access_token")
refresh_token = controller.get("refresh_token")
if refresh_token and access_token and "user" not in st.session_state:
    try:
        user = supabase.auth.get_user(access_token)
    except Exception as e:
        new_session = supabase.auth.refresh_session(refresh_token).session
        controller.set("access_token", new_session.access_token)
        controller.set("refresh_token", new_session.refresh_token)
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
    st.warning("Please log in to access the recipe library.")
    st.stop()

################################################# 

if st.session_state.user is None:
    st.warning("Please log in to access the shopping list generator.")
    st.stop()

# Calculate the date of the next Monday
today = date.today()
days_until_monday = (7 - today.weekday()) % 7
next_monday = today + timedelta(days=days_until_monday)

def fetch_meal_plan():
    response = supabase.table("meal_plans").select("*, recipes(*)").eq("user", st.session_state.user.id).eq("week", next_monday).execute()
    if not response:
        st.error(f"Error fetching meal plans.")
        return []
    return response.data

meal_plan = fetch_meal_plan()

if not meal_plan:
    st.warning("No recipes planned for the next 7 days.")
    st.stop()

# 2. Create prompt for Groq (leave out instructions!)
def format_recipe(r):
    return f"""{r["name"]} with {', '.join(r.get("ingredients", []))};"""

prompt = "You are a helpful cooking assistant. Based on the following recipes, generate a combined shopping list grouped by category: vegetables, other items, and things that are probably at home already. Avoid duplicates. Do not add any translations or explanations in parentheses. Keep ingredient names exactly as in the input, even if they're not English. Ingredients like spices, oils, sauces (e.g. soy sauce, tahin, sriracha, peanut butter, vinegar, maple syrup, curry powder, etc.) should go under \"things that are probably at home already\", unless they are very uncommon. Group logically. Output only the list.\n\n Recipes: \n"

for entry in meal_plan:
    prompt += format_recipe(entry["recipes"]) + "\n"

st.markdown("### 📝 Prompt for Groq"
             f" (for {len(meal_plan)} recipes):")
st.markdown(f"```python\n{prompt}```")

st.divider()

st.markdown(f"Ask Groq for shopping list or paste prompt into ChatGPT.")

#prompt += "Please format the result clearly with bullet points under each category."

# 3. Call Groq API
if st.button("Generate Shopping List"):
    with st.spinner("Asking Groq for help..."):
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # or llama3-70b if available
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        result = response.choices[0].message.content

        st.markdown("### 🧾 Shopping List")
        st.markdown(result)
