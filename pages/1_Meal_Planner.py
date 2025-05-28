import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
from streamlit_cookies_controller import CookieController
import time
from supabase import create_client

st.set_page_config(page_title="Meal Planner", layout="centered")
st.title("📅 Meal Planner")

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
    st.warning("Please log in to access the meal planner.")
    st.stop()

################################################# 

def get_start_of_week(d: date):
    return d - timedelta(days=d.weekday())

today = date.today()
selected_date = st.date_input("Select any day in the target week", today)
week_start = get_start_of_week(selected_date)
week_start_str = week_start.strftime("%Y-%m-%d")

st.markdown(f"### Plan 5 recipes for the week starting **{week_start_str}**")

# def fetch_recipes():
#     response = supabase.table("recipes").select("*").eq("author", st.session_state.user.id).execute()
#     if not response:
#         st.error(f"Error fetching recipes.")
#         return []
#     return response.data

def fetch_recipes():
    def merge_recipes(user_recipes, public_recipes):
        merged = {recipe["id"]: recipe for recipe in user_recipes}
        for recipe in public_recipes:
            if recipe["id"] not in merged:
                merged[recipe["id"]] = recipe
        return list(merged.values())
    user_recipes = supabase.table("recipes").select("*").eq("author", st.session_state.user.id).execute()
    public_recipes = supabase.table("recipes").select("*").eq("public", True).execute()
    if not user_recipes:
        st.error(f"Error fetching recipes: {user_recipes.error.message}")
        return []
    return merge_recipes(user_recipes.data, public_recipes.data)

def fetch_meal_plan():
    response = supabase.table("meal_plans").select("*, recipes(*)").eq("user", st.session_state.user.id).eq("week", week_start_str).execute()
    if not response:
        st.error(f"Error fetching meal plans.")
        return []
    return response.data

recipes = fetch_recipes()
meal_plan = fetch_meal_plan()

if not recipes:
    st.warning("No recipes found in the library. Please add recipes first!")
    st.stop()

# Prepare recipe names list with an empty option
recipe_names = [""] + [r["name"] for r in recipes]

# Filter meal plans for the selected week
current_week_entries = {entry.get("day"): entry for entry in meal_plan}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

with st.form("meal_planner_form"):
    for i, day in enumerate(days):
        if i not in current_week_entries:
            recipe_name = ""
        else:
            recipe_id = current_week_entries[i].get("recipe")
            recipe_name = current_week_entries[i].get("recipes").get("name")

        meal = st.selectbox(f"{day}'s meal", options=recipe_names, index=recipe_names.index(recipe_name) if recipe_name in recipe_names else 0, key=f"meal_{week_start_str}_{i}")

    submitted = st.form_submit_button("Save Meal Plan")

    if submitted:
        for i in range(5):
            meal = st.session_state.get(f"meal_{week_start_str}_{i}")
            if meal:
                # Check if the meal already exists in the current week entries
                if i in current_week_entries:
                    # Update the meal plan entry if the recipe has changed
                    if current_week_entries[i]["recipes"]["name"] != meal:
                        data = {"recipe": next((r["id"] for r in recipes if r["name"] == meal), None)}
                        response = supabase.table("meal_plans").update(
                            data
                        ).eq("id", current_week_entries[i]["id"]).execute()
                else:
                    # Insert a new meal plan entry if it doesn't exist
                    supabase.table("meal_plans").insert(
                        {"week": week_start_str, "day": i, "recipe": next((r["id"] for r in recipes if r["name"] == meal), None), "user": st.session_state.user.id}
                    ).execute()
            else:
                # If the meal is not set, delete the entry if it exists
                if i in current_week_entries:
                    supabase.table("meal_plans").delete().eq("id", current_week_entries[i]["id"]).execute()

        st.success(f"Meal plan for week {week_start_str} saved!")
        st.rerun()

st.divider()

# Display current plan in a table
st.markdown(f"### Current meal plan for week {week_start_str}")

df = pd.DataFrame({
    "Day": days,
    "Recipe": [current_week_entries[i]["recipes"]["name"] if i in current_week_entries else "" for i in range(5)],
    "Rate": [current_week_entries[i]["rating"] if i in current_week_entries else None for i in range(5)],
    "Comment": [current_week_entries[i]["comment"] if i in current_week_entries else None for i in range(5)],
})

# Allow editing of ratings and comments
edited_df = st.data_editor(
    df,
    column_config={
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

if st.button("Save feedback"):
    for i, day in enumerate(days):
        if i in current_week_entries:
            entry_id = current_week_entries[i]["id"]
            updated_rating = edited_df.at[i, "Rate"]
            updated_comment = edited_df.at[i, "Comment"]

            # Check if rating or comment has changed
            if (
                updated_rating != current_week_entries[i].get("rating") or
                updated_comment != current_week_entries[i].get("comment")
            ):
                supabase.table("meal_plans").update({
                    "rating": int(updated_rating) or None,
                    "comment": updated_comment or None
                }).eq("id", entry_id).execute()

    st.success("Feedback saved successfully!")
    st.rerun()

st.markdown("#### Recipe Details")

# Unter der Tabelle: Ausklappbare Details pro Tag
for i, entry in current_week_entries.items():
    recipe_name = entry["recipes"]["name"]
    with st.expander(f"**{days[i]} - {recipe_name}**"):
        st.write("")
        st.write(f"**Ingredients:** {', '.join(entry['recipes']['ingredients'])}")
        st.info(f"**Instructions:** {entry['recipes']['instructions']}")
    
st.divider()

st.markdown("#### Approve Meal Plan for the Week")

sentiment_mapping = [":material/thumb_down:", ":material/thumb_up:"]
selected = st.feedback("thumbs")