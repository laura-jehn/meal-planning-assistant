import streamlit as st
from datetime import date, timedelta

from utils import load_all_state, save_all_state

st.set_page_config(page_title="Meal Planner", layout="centered")
st.title("📅 Meal Planner")

if "initialized" not in st.session_state:
    recipes, meal_plan = load_all_state()
    st.session_state.recipes = recipes
    st.session_state.meal_plan = meal_plan
    st.session_state.initialized = True

recipes = st.session_state.recipes
meal_plan = st.session_state.meal_plan

if not recipes:
    st.warning("No recipes found in the library. Please add recipes first!")
    st.stop()

# Prepare recipe names list with an empty option
recipe_names = [""] + [r["name"] for r in recipes]

def get_start_of_week(d: date):
    return d - timedelta(days=d.weekday())

today = date.today()
selected_date = st.date_input("Select any day in the target week", today)
week_start = get_start_of_week(selected_date)
week_start_str = week_start.strftime("%Y-%m-%d")

st.markdown(f"### Plan 5 recipes for the week starting **{week_start_str}**")

existing_plan = st.session_state.meal_plan.get(week_start_str, [""] * 5)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

with st.form("meal_planner_form"):
    selected_meals = []
    for i, day in enumerate(days):
        meal = st.selectbox(f"{day}'s meal", options=recipe_names, index=recipe_names.index(existing_plan[i]) if existing_plan[i] in recipe_names else 0, key=f"meal_{week_start_str}_{i}")
        selected_meals.append(meal)

    submitted = st.form_submit_button("Save Meal Plan")

    if submitted:
        st.session_state.meal_plan[week_start_str] = selected_meals
        st.success(f"Meal plan for week {week_start_str} saved!")
        save_all_state(st.session_state.recipes, st.session_state.meal_plan)
        st.rerun()

st.divider()

# Display current plan in a table
st.markdown(f"### Current meal plan for week {week_start_str}")

# Initialize session state
if "feedback" not in st.session_state:
    st.session_state.feedback = {
        day: {"star": 0, "comment": ""} for day in days
    }

import pandas as pd
df = pd.DataFrame({
    "Day": days,
    "Recipe": existing_plan,
    "Rate": [st.session_state.feedback[day]["star"] for day in days],
    "Comment": [st.session_state.feedback[day]["comment"] for day in days]
})

#TODO: save feedback to recipe as well as meal plan!

edited_df = st.data_editor(
    df,
    column_config={
        "Day": "",
        "Recipe": st.column_config.SelectboxColumn(
            "Recipe",
            options=recipe_names,
        ),
        "Rate": st.column_config.NumberColumn(
            "Your rating",
            min_value=0,
            max_value=5,
            step=1,
            format="%d ⭐",
        ),
        "Comment": st.column_config.TextColumn(
            "Comment",
            max_chars=100,
        ),
    },
    hide_index=True,
)

# Unter der Tabelle: Ausklappbare Details pro Tag
for day, recipe in zip(days, existing_plan):
    recipe = next((r for r in recipes if r["name"] == recipe), None)
    if recipe is None:
        st.markdown(f"#### {day} - No recipe planned")
        continue
    with st.expander(f"{day} - {recipe['name']} details"):
        st.write(f"**Protein:** {recipe.get('protein', 'N/A')}")
        st.write(f"**Sauce:** {recipe.get('sauce', 'N/A')}")
        st.write(f"**Vegetables:** {', '.join(recipe.get('veggies', []))}")
        st.write(f"**Toppings:** {', '.join(recipe.get('toppings', []))}")
        st.write(f"**Notes:** {recipe.get('notes', '')}")
        st.write(f"**Instructions:** {recipe.get('instructions', '')}")