import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import date, timedelta

from utils import load_all_state, save_all_state

st.set_page_config(page_title="Shopping List", layout="centered")

st.title("🛒 Shopping List Generator")

if "initialized" not in st.session_state:
    recipes, meal_plan = load_all_state()
    st.session_state.recipes = recipes
    st.session_state.meal_plan = meal_plan
    st.session_state.initialized = True

meal_plan = st.session_state.meal_plan

load_dotenv()
groq_client = Groq(
  api_key=os.getenv("GROQ_API_KEY")
)

# Calculate the date of the next Monday
today = date.today()
days_until_monday = (7 - today.weekday()) % 7
next_monday = today + timedelta(days=days_until_monday)

recipe_names = meal_plan.get(str(next_monday), [])
planned_recipes = []

for recipe_name in recipe_names:
    recipe = next((r for r in st.session_state.recipes if r["name"] == recipe_name), None)
    if recipe:
        planned_recipes.append(recipe)

if not planned_recipes:
    st.warning("No recipes planned for the next 7 days.")
    st.stop()

# 2. Create prompt for Groq (leave out instructions!)
def format_recipe(r):
    return f"""Recipe: {r["name"]} with
    {r.get("protein", "")}, {r.get("sauce", "")}, {', '.join(r.get("veggies", []))}, {', '.join(r.get("toppings", []))}, {r.get("notes", "")}
    """

prompt = "You are a helpful cooking assistant. Based on the following recipes, generate a combined shopping list grouped by category: vegetables, other items, and things that are probably at home already. Avoid duplicates. Make sure only vegetables are in the vegetable category. Do not add any translations or explanations in parentheses. Keep ingredient names exactly as in the input, even if they're not English Ingredients like spices, oils, sauces (e.g. soy sauce, tahin, sriracha, peanut butter, vinegar, maple syrup, curry powder, etc.) should go under \"things that are probably at home already\", unless they are very uncommon. Group logically. Output only the list.\n\n"

for r in planned_recipes:
    prompt += format_recipe(r) + "\n\n"

st.markdown("### 📝 Prompt for Groq"
             f" (for {len(planned_recipes)} recipes):")
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
