import streamlit as st
import time
from utils import *
from recipe_scrapers import scrape_me

st.set_page_config(page_title="Recipe Library", layout="centered")
st.title("📚 Recipe Library")

supabase, controller = authenticate()
show_login(controller)

if "user" not in st.session_state:
    st.warning("Please log in to access the recipe library.")
    st.stop()

# Form for URL input
with st.form("recipe_form"):
    url = st.text_input("Paste the recipe URL here:")
    public = st.checkbox("Make recipe publicly available")
    submit = st.form_submit_button("Add recipe from URL")

if submit:
    try:
        scraper = scrape_me(url)

        # Extract fields
        name = scraper.title()
        ingredients = scraper.ingredients()
        instructions = scraper.instructions()

        new_recipe = {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "author": st.session_state.user.id,
            "public": public
        }

        response = supabase.table("recipes").insert(new_recipe).execute()
        st.success(f"Recipe '{name}' added!")
        # Show result
        st.markdown("**Ingredients:**")
        st.write(ingredients)
        st.markdown("**Instructions:**")
        st.write(instructions)
        time.sleep(10)
        st.rerun()

    except Exception as e:
        st.error(f"Failed to scrape recipe: {e}")

def fetch_my_recipes():
    # def merge_recipes(user_recipes, public_recipes):
    #     merged = {recipe["id"]: recipe for recipe in user_recipes}
    #     for recipe in public_recipes:
    #         if recipe["id"] not in merged:
    #             merged[recipe["id"]] = recipe
    #     return list(merged.values())
    try:
        user_recipes = supabase.table("recipes").select("*").eq("author", st.session_state.user.id).execute()
    except Exception as e:
        st.error(f"Error fetching user recipes: {e}")
        return []
    return user_recipes.data

def fetch_public_recipes():
    try:
        public_recipes = supabase.table("recipes").select("*").eq("public", True).neq("author", st.session_state.user.id).execute()
    except Exception as e:
        st.error(f"Error fetching user recipes: {e}")
        return []
    return public_recipes.data


recipes = fetch_my_recipes()
public_recipes = fetch_public_recipes()

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
    public = st.checkbox("Make recipe publicly available")

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
                "author": st.session_state.user.id,
                "public": public
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

        if save:
            updated = {
                "name": name.strip(),
                "ingredients" : [ing.strip() for ing in ingredients.split(",")],
                "instructions": instructions or None,
            }

            try:
                response = supabase.table("recipes").update(updated).eq("id", recipe["id"]).execute()
            except Exception as e:
                st.error(f"Error updating recipe: {e}")

            st.session_state.edit_index = None
            st.success("Recipe updated!")
            st.rerun()

        if cancel:
            st.session_state.edit_index = None
            st.info("Editing canceled.")
            st.rerun()

# --- DISPLAY EXISTING RECIPES ---
st.subheader("📖 My Recipes")

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
    st.info("No recipes yet. Create one above or add one from below!")

st.subheader("🌍 Public Recipes")

if public_recipes:
    for i, recipe in enumerate(public_recipes):
        with st.expander(f"{i+1}. **{recipe['name']}**"):
            st.write(f"**Ingredients:** {', '.join(recipe['ingredients'])}")
            st.info(f"**Instructions:** {recipe['instructions']}")

            if st.button("💾 Save to My Recipes", key=f"save_public_{i}"):
                try:
                    new_recipe = {
                        "name": recipe["name"],
                        "ingredients": recipe["ingredients"],
                        "instructions": recipe["instructions"],
                        "author": st.session_state.user.id
                    }
                    response = supabase.table("recipes").insert(new_recipe).execute()
                    st.success(f"Recipe '{recipe['name']}' saved to your recipes!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving recipe: {e}")
