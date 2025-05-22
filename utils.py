import json
import os

RECIPE_FILE = "recipes.json"
PLAN_FILE = "meal_plan.json"

def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_all_state():
    recipes = load_data(RECIPE_FILE, [])
    meal_plan = load_data(PLAN_FILE, {})
    return recipes, meal_plan

def save_all_state(recipes, meal_plan):
    save_data(RECIPE_FILE, recipes)
    save_data(PLAN_FILE, meal_plan)
