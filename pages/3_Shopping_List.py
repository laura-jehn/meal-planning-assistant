import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import date, timedelta

from supabase import create_client, Client

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
groq_client = Groq(
  api_key=os.getenv("GROQ_API_KEY")
)

st.set_page_config(page_title="Shopping List", layout="centered")
st.title("🛒 Shopping List Generator")

# Calculate the date of the next Monday
today = date.today()
days_until_monday = (7 - today.weekday()) % 7
next_monday = today + timedelta(days=days_until_monday)

def fetch_meal_plan():
    response = supabase.table("meal_plans").select("*, recipes(*)").eq("week", next_monday).execute()
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
