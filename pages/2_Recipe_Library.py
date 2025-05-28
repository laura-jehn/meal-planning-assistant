import streamlit as st
from streamlit_cookies_controller import CookieController
import time
from datetime import datetime, timedelta
from supabase import create_client

st.set_page_config(page_title="Recipe Library", layout="centered")
st.title("📚 Recipe Library")

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

if "user" in st.session_state:
    st.sidebar.write(f"👋 Logged in as: {st.session_state.user.email}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        expires_at = datetime.now() + timedelta(days=-7)
        controller.set(cookie_name, "", expires=expires_at)
        time.sleep(1)
        st.rerun()

if "user" not in st.session_state:
    st.warning("Please log in to access the recipe library.")
    st.stop()

################################################# 

def fetch_recipes():
    response = supabase.table("recipes").select("*").execute()
    if not response:
        st.error(f"Error fetching recipes: {response.error.message}")
        return []
    return response.data

# Fetch recipes and initialize session state
recipes = fetch_recipes()

# --- CATEGORY OPTIONS (with empty option for optionality) ---
TYPES = [""] + ["salad", "soup", "wraps/burrito", "bowl (graupe)", "veggie+base+protein", "potato+schnitzel+veggie"]
BASES = [""] + ["rice noodles", "rice", "pasta", "gnocchi", "tortellini", "rice paper"]
PROTEINS = [""] + ["lentils", "tofu", "kichererbsen", "fake chicken", "veggie hack", "kidney beans"]
SAUCES = [""] + ["peanut butter", "tahin", "honig/senf", "sahne", "yogurt"]
VEGGIES = ["blumenkohl", "karotten", "pilze", "chinakohl", "spinat", "brokkoli", "grüner spargel", "sweet potato", "lauch", "kartoffel", "tomaten", "pak choi"]
TOPPINGS = ["lauchzwiebel", "sesam", "cashews/peanut", "petersilie", "koriander"]

# --- FORM FOR NEW RECIPE ---
with st.form("create_recipe"):
    st.subheader("📝 Create a New Recipe")

    name = st.text_input("Recipe Name", placeholder="Required", key="name")
    base = st.selectbox("Base (optional)", BASES, key="base")
    protein = st.selectbox("Protein (optional)", PROTEINS, key="protein")
    sauce = st.selectbox("Sauce (optional)", SAUCES, key="sauce")
    veggies = st.multiselect("Vegetables (optional)", VEGGIES, key="veggies")
    toppings = st.multiselect("Toppings (optional)", TOPPINGS, key="toppings")
    notes = st.text_area("Additional Ingredients", key="notes")
    instructions = st.text_area("Instructions", key="instructions")

    submitted = st.form_submit_button("➕ Add Recipe")

    if submitted:
        if not st.session_state.name.strip():
            st.error("Please enter a recipe name.")
        else:
            # aggregate ingredients
            ingredients = []
            if st.session_state.protein:
                ingredients.append(st.session_state.protein)
            if st.session_state.base:
                ingredients.append(st.session_state.base)
            if st.session_state.sauce:
                ingredients.append(st.session_state.sauce)
            ingredients.extend(st.session_state.veggies)
            ingredients.extend(st.session_state.toppings)
            
            notes_array = [note.strip() for note in st.session_state.notes.split(",") if note.strip()] if st.session_state.notes else []
            ingredients.extend(notes_array)
            
            new_recipe = {
                "name": st.session_state.name.strip(),
                "ingredients": ingredients,
                "instructions": st.session_state.instructions or None,
            }

            response = supabase.table("recipes").insert(new_recipe).execute()
            st.success(f"Recipe '{new_recipe['name']}' added!")
            st.rerun()

st.divider()

edit_index = st.session_state.get("edit_index", None)

if edit_index is not None:
    recipe = recipes[edit_index]
    st.subheader(f"✏️ Edit Recipe: {recipe['name']}")

    with st.form("edit_recipe_form"):
        
        name = st.text_input("Recipe Name", value=recipe["name"])
        ingredients = st.text_input("Ingredients", value=", ".join(recipe.get("ingredients", [])))
        instructions = st.text_area("Instructions", value=recipe.get("instructions", ""))

        col1, col2 = st.columns(2)
        save = col1.form_submit_button("💾 Save Changes")
        cancel = col2.form_submit_button("❌ Cancel")

        print(recipe)

        if save:
            updated = {
                "name": name.strip(),
                "ingredients" : [ing.strip() for ing in ingredients.split(",")],
                "instructions": instructions or None,
            }

            response = supabase.table("recipes").update(updated).eq("id", recipe["id"]).execute()
            if not response:
                st.error(f"Error updating recipe: {response.error.message}")
            st.session_state.edit_index = None
            st.success("Recipe updated!")
            st.rerun()

        if cancel:
            st.session_state.edit_index = None
            st.info("Editing canceled.")
            st.rerun()

# --- DISPLAY EXISTING RECIPES ---
st.subheader("📖 Saved Recipes")

if recipes:
    for i, recipe in enumerate(recipes):
        with st.expander(f"{i+1}. **{recipe['name']}**"):
            st.write(f"**Ingredients:** {', '.join(recipe['ingredients'])}")
            st.info(f"**Instructions:** {recipe['instructions']}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    response = supabase.table("recipes").delete().eq("id", recipe["id"]).execute()
                    if not response:
                        st.error(f"Error deleting recipe: {response.error.message}")
                    st.success("Deleted.")
                    st.rerun()
else:
    st.info("No recipes yet. Create one above!")
