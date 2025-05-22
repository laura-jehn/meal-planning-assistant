import streamlit as st

from utils import load_all_state, save_all_state

if "initialized" not in st.session_state:
    recipes, meal_plan = load_all_state()
    st.session_state.recipes = recipes
    st.session_state.meal_plan = meal_plan
    st.session_state.initialized = True

recipes = st.session_state.recipes

# Set page title and layout
st.set_page_config(page_title="Recipe Library", layout="centered")

st.title("📚 Recipe Library")
st.markdown("Create and store abstract meal recipes.")

# --- CATEGORY OPTIONS (with empty option for optionality) ---
TYPES = [""] + ["salad", "soup", "wraps/burrito", "bowl (graupe)", "veggie+base+protein", "potato+schnitzel+veggie"]
BASES = [""] + ["rice noodles", "rice", "pasta", "gnocchi", "tortellini", "rice paper"]
PROTEINS = [""] + ["lentils", "tofu", "kichererbsen", "fake chicken", "veggie hack", "kidney beans"]
SAUCES = [""] + ["peanut", "tahin", "honig/senf", "sahne", "yogurt"]
VEGGIES = ["blumenkohl", "karotten", "pilze", "chinakohl", "spinat", "brokkoli", "grüner spargel", "sweet potato", "lauch", "kartoffel", "tomaten", "pak choi"]
TOPPINGS = ["lauchzwiebel", "sesam", "cashews/peanut", "petersilie", "koriander"]

# --- FORM FOR NEW RECIPE ---
with st.form("create_recipe"):
    st.subheader("📝 Create a New Recipe")

    name = st.text_input("Recipe Name", placeholder="Required", key="name")
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
            new_recipe = {
                "name": st.session_state.name.strip(),
                "protein": st.session_state.protein if st.session_state.protein else None,
                "sauce": st.session_state.sauce if st.session_state.sauce else None,
                "veggies": st.session_state.veggies,
                "toppings": st.session_state.toppings,
                "notes": st.session_state.notes or None,
                "instructions": st.session_state.instructions or None,
            }
            st.session_state.recipes.append(new_recipe)
            st.success(f"Recipe '{new_recipe['name']}' added!")
            save_all_state(st.session_state.recipes, st.session_state.meal_plan)

st.divider()

edit_index = st.session_state.get("edit_index", None)

if edit_index is not None:
    recipe = recipes[edit_index]
    st.subheader(f"✏️ Edit Recipe: {recipe['name']}")

    with st.form("edit_recipe_form"):
        
        name = st.text_input("Recipe Name", value=recipe["name"])
        protein = st.text_input("Protein", value=recipe.get("protein", ""))
        sauce = st.text_input("Sauce", value=recipe.get("sauce", ""))
        veggies = st.text_input("Vegetables", value=", ".join(recipe.get("veggies", [])))
        toppings = st.text_input("Toppings", value=", ".join(recipe.get("toppings", [])))
        notes = st.text_area("Additional Ingredients", value=recipe.get("notes", ""))
        instructions = st.text_area("Instructions", value=recipe.get("instructions", ""))

        col1, col2 = st.columns(2)
        save = col1.form_submit_button("💾 Save Changes")
        cancel = col2.form_submit_button("❌ Cancel")

        if save:
            updated = {
                "name": name.strip(),
                "protein": protein.strip() if protein else None,
                "sauce": sauce.strip() if sauce else None,
                "veggies": [v.strip() for v in veggies.split(",") if v.strip()],
                "toppings": [t.strip() for t in toppings.split(",") if t.strip()],
                "notes": notes or None,
                "instructions": instructions or None,
            }
            st.session_state.recipes[edit_index] = updated
            st.session_state.edit_index = None
            save_all_state(st.session_state.recipes, st.session_state.meal_plan)
            st.success("Recipe updated!")
            st.rerun()

        if cancel:
            st.session_state.edit_index = None
            st.info("Editing canceled.")
            st.rerun()

# --- DISPLAY EXISTING RECIPES ---
st.subheader("📖 Saved Recipes")

if st.session_state.recipes:
    for i, recipe in enumerate(st.session_state.recipes):
        with st.expander(f"{i+1}. {recipe['name']}"):
            if recipe.get("protein"): st.write(f"**Protein:** {recipe['protein']}")
            if recipe.get("sauce"): st.write(f"**Sauce:** {recipe['sauce']}")
            if recipe.get("veggies"): st.write(f"**Vegetables:** {', '.join(recipe['veggies'])}")
            if recipe.get("toppings"): st.write(f"**Toppings:** {', '.join(recipe['toppings'])}")
            if recipe.get("notes"): st.info(f"💬 {recipe['notes']}")
            if recipe.get("instructions"): st.write(f"**Instructions:** {recipe['instructions']}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.recipes.pop(i)
                    save_all_state(st.session_state.recipes, st.session_state.meal_plan)
                    st.success("Deleted.")
                    st.rerun()
else:
    st.info("No recipes yet. Create one above!")
