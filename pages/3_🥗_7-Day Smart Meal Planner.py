import pandas as pd
import random
from datetime import datetime, timedelta
import os
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="7-Day Smart Meal Planner", page_icon="🥗", layout="wide")

# ---------- Sidebar Settings ----------
with st.sidebar:
    st.markdown("### 🍎 Dietary Preferences")
    preferences = st.multiselect("Dietary Preferences", ["Vegetarian", "High-Protein", "Low-Carb", "Gluten-Free"], help="Select your dietary preferences")
    cuisine = st.selectbox("Cuisine Type", ["Any", "Asian", "Mediterranean", "American"], help="Select preferred cuisine")
    difficulty = st.selectbox("Cooking Difficulty", ["Any", "Easy", "Medium", "Hard"], help="Select cooking difficulty")
    st.markdown("### 🚫 Excluded Ingredients")
    exclude_ingredients = st.text_input("Enter ingredients to exclude (comma-separated)", "", help="e.g., beef, spinach").split(",")
    exclude_ingredients = [item.strip().lower() for item in exclude_ingredients if item.strip()]
    st.markdown("### 📊 Nutrition Goals")
    target_calories = st.number_input("Daily Calorie Goal (kcal)", 1000, 5000, 2000)
    target_protein = st.number_input("Daily Protein Goal (g)", 10, 200, 50)
    target_carbohydrates = st.number_input("Daily Carbohydrate Goal (g)", 10, 500, 200)
    target_fat = st.number_input("Daily Fat Goal (g)", 10, 200, 70)
    # Favorites
    st.markdown("### ⭐ Favorites")
    if "favorites" not in st.session_state:
        st.session_state["favorites"] = []
    if st.session_state["favorites"]:
        for fav_dish in st.session_state["favorites"]:
            if st.button(fav_dish, key=f"fav_link_{fav_dish}", help="Click to view dish details"):
                st.session_state["scroll_to_dish"] = fav_dish
                st.rerun()
        if st.button("⚠️ **Clear Favorites**", key="clear_favorites", help="Remove all favorite dishes"):
            st.session_state["favorites"] = []
            st.success("All favorites cleared!")
            st.rerun()
    else:
        st.write("No favorite dishes yet")
    st.markdown("### 🖼️ Image Settings")
    img_size = st.slider("Image Width (px)", 100, 800, 330, 10)

# ---------- CSS Styles (Enhanced Aesthetics with Padding Fix and Button Redesign) ----------
st.markdown("""
<style>
body {
    background-color: #f9fafb;
    font-family: 'Inter', sans-serif;
    color: #1e293b;
}
h1 {
    font-size: 2.8rem;
    font-weight: 700;
    text-align: center;
    margin: 1rem 0;
    color: #1e293b;
}
.title {
    font-size: 1.6rem;
    font-weight: 600;
    margin: 1.2rem 0 0.8rem;
    color: #1e293b;
}
.subtitle {
    font-size: 1.1rem;
    font-weight: 500;
    text-align: center;
    color: #6c757d;
    margin: 0.5rem 0;
}
hr.divider {
    border: none;
    border-top: 2px solid #e5e7eb;
    margin: 1rem 0;
}
.meal-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}
.meal-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
}
.meal-card:hover {
    transform: translateY(-4px);
}
.meal-card img {
    width: 100%;
    height: auto;
    max-height: 180px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 0.8rem;
}
.meal-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.meal-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.meal-calories {
    color: #22c55e;
    font-size: 0.9rem;
    font-weight: 500;
    background: #f0fdf4;
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
}
.meal-details {
    color: #475569;
    font-size: 0.85rem;
    line-height: 1.5;
}
.meal-details strong {
    color: #1e293b;
    font-weight: 600;
}
.refresh-button, .favorite-button {
    background: #22c55e;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    text-align: center;
    transition: background 0.2s ease;
    margin-top: 0.6rem;
}
.refresh-button:hover, .favorite-button:hover {
    background: #16a34a;
}
.clear-favorites-button {
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: background 0.2s ease;
    margin-top: 0.6rem;
    width: 100%;
}
.clear-favorites-button:hover {
    background: #dc2626;
}
.download-section {
    background: #e5e7eb;
    padding: 1rem;
    border-radius: 10px;
    margin: 1.5rem 0;
    text-align: center;
}
.download-section a {
    color: #1e293b;
    font-weight: 500;
    text-decoration: none;
    transition: color 0.2s ease;
}
.download-section a:hover {
    color: #16a34a;
}
.stButton>button {
    background: #22c55e;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    border: 1px solid #15803d;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}
.stButton>button:hover {
    background: #16a34a;
    transform: scale(1.05);
}
.stForm {
    background: #ffffff;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.stSlider label, .stSelectbox label, .stRadio label, .stCheckbox label {
    color: #1e293b;
    font-weight: 500;
    font-size: 0.9rem;
}
.stSelectbox > div > div > select {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.5rem;
    font-size: 0.9rem;
    color: #1e293b;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.stSelectbox > div > div > select:focus {
    border-color: #16a34a;
    outline: none;
}
.chart-container {
    padding-right: 20px !important;
}
@media (max-width: 600px) {
    .meal-card img {
        max-height: 120px;
    }
    .meal-container {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------- Recipe Database ----------
RECIPE_DB = {
    "Breakfast": {
        "Oats & Berries Bowl": {"calories": 320, "carbohydrates": 45, "protein": 12, "fat": 8,
                                "ingredients": "Oats, mixed berries, almond milk, honey",
                                "steps": "Mix oats, berries, almond milk, and honey. Refrigerate overnight.",
                                "tags": ["Vegetarian", "Gluten-Free"]},
        "Egg & Avocado Toast": {"calories": 380, "carbohydrates": 30, "protein": 18, "fat": 22,
                                "ingredients": "Whole-wheat toast, eggs, avocado, lemon juice",
                                "steps": "Toast bread, fry eggs, mash avocado with lemon juice, spread on toast.",
                                "tags": ["High-Protein"]},
        "Greek Yogurt Parfait": {"calories": 260, "carbohydrates": 35, "protein": 15, "fat": 6,
                                 "ingredients": "Greek yogurt, granola, mixed berries, chia seeds",
                                 "steps": "Layer yogurt, granola, and berries in a glass. Top with chia seeds.",
                                 "tags": ["High-Protein", "Vegetarian"]},
    },
    "Lunch": {
        "Grilled Chicken Salad": {"calories": 420, "carbohydrates": 20, "protein": 35, "fat": 22,
                                  "ingredients": "Chicken breast, lettuce, tomato, cucumber, olive oil",
                                  "steps": "Grill chicken, chop vegetables, toss with olive oil and seasoning.",
                                  "tags": ["High-Protein", "Low-Carb"]},
        "Tofu Stir-fry": {"calories": 390, "carbohydrates": 35, "protein": 20, "fat": 18,
                          "ingredients": "Tofu, broccoli, bell pepper, soy sauce, sesame oil",
                          "steps": "Sauté tofu in sesame oil, add vegetables and soy sauce, stir-fry until tender.",
                          "tags": ["Vegetarian", "High-Protein"]},
        "Quinoa & Black Bean Bowl": {"calories": 400, "carbohydrates": 55, "protein": 15, "fat": 10,
                                     "ingredients": "Quinoa, black beans, corn, avocado, lime",
                                     "steps": "Cook quinoa, mix with beans, corn, and avocado. Squeeze lime on top.",
                                     "tags": ["Vegetarian", "Gluten-Free"]},
    },
    "Dinner": {
        "Baked Cod & Veg": {"calories": 380, "carbohydrates": 25, "protein": 32, "fat": 14,
                            "ingredients": "Cod fillet, asparagus, garlic, lemon, olive oil",
                            "steps": "Season cod, place with asparagus on tray, drizzle with olive oil, bake at 200°C for 15 min.",
                            "tags": ["High-Protein", "Low-Carb"]},
        "Lentil Curry": {"calories": 410, "carbohydrates": 45, "protein": 20, "fat": 12,
                         "ingredients": "Lentils, coconut milk, curry paste, onion, spinach",
                         "steps": "Sauté onion, add curry paste, lentils, and coconut milk. Simmer 20 min, add spinach.",
                         "tags": ["Vegetarian", "High-Protein"]},
        "Beef Stir-fry": {"calories": 450, "carbohydrates": 30, "protein": 28, "fat": 20,
                          "ingredients": "Beef strips, zucchini, carrots, soy sauce, ginger",
                          "steps": "Stir-fry beef with ginger, add vegetables and soy sauce, cook until tender.",
                          "tags": ["High-Protein"]},
    }
}

# ---------- Recipe Generation Function (Supports Excluded Ingredients) ----------
def build_recipes(user, preferences, cuisine, difficulty, exclude_ingredients):
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    offset = 0 if user["start_choice"] == "Today" else 1
    meals = ["Breakfast", "Lunch", "Dinner"]
    recipes = []
    days = [(base_date + timedelta(days=i + offset)).strftime("%a %m-%d") for i in range(7)]
    
    # Adjust preferences based on BMI
    bmi = user["weight"] / (user["height"] ** 2)
    adjusted_preferences = preferences.copy()
    if bmi >= 25 and "Low-Carb" not in adjusted_preferences:
        adjusted_preferences.append("Low-Carb")
    elif bmi < 18.5 and "High-Protein" not in adjusted_preferences:
        adjusted_preferences.append("High-Protein")

    for day in days:
        for meal in meals:
            available_dishes = list(RECIPE_DB[meal].keys())
            if adjusted_preferences or cuisine or difficulty or exclude_ingredients:
                available_dishes = [
                    dish for dish in available_dishes
                    if (not adjusted_preferences or any(tag in RECIPE_DB[meal][dish]["tags"] for tag in adjusted_preferences)) and
                    (not cuisine or ("Cuisine" in RECIPE_DB[meal][dish] and RECIPE_DB[meal][dish]["Cuisine"] == cuisine)) and
                    (not difficulty or ("Difficulty" in RECIPE_DB[meal][dish] and RECIPE_DB[meal][dish]["Difficulty"] == difficulty)) and
                    (not exclude_ingredients or not any(ing.lower() in RECIPE_DB[meal][dish]["ingredients"].lower() for ing in exclude_ingredients))
                ]
            if not available_dishes:
                available_dishes = list(RECIPE_DB[meal].keys())
            dish = random.choice(available_dishes)
            data = RECIPE_DB[meal][dish]
            recipes.append({
                "day": day, "meal": meal, "dish": dish,
                "calories": data["calories"], "carbohydrates": data["carbohydrates"],
                "protein": data["protein"], "fat": data["fat"],
                "ingredients": data["ingredients"], "steps": data["steps"]
            })
    df = pd.DataFrame(recipes)
    df["day"] = pd.Categorical(df["day"], categories=days, ordered=True)
    return df

# ---------- Export CSV Utility Function ----------
def to_csv(df):
    return df.to_csv(index=False).encode()

# ---------- Main Interface ----------
st.markdown(
    """
    <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
        🥗 7-Day Smart Meal Planner
    </h1>
    <p class='subtitle'>Customize your weekly meal plan based on your preferences and personal information!</p>
    <hr class='divider'>
    """,
    unsafe_allow_html=True,
)

# ---------- User Information Form ----------
with st.form("plan_form"):
    st.markdown("##### 🪪 Personal Information")
    c1, c2, c3 = st.columns(3)
    with c1:
        gender = st.selectbox("⚧️ Gender", ["Male", "Female"])
        age = st.slider("🎂 Age", 0, 120, 30)
    with c2:
        height = st.slider("📏 Height (m)", 0.5, 2.5, 1.7, 0.01)
        weight = st.slider("⚖️ Weight (kg)", 20.0, 200.0, 70.0, 0.1)
    with c3:
        family_history = st.selectbox("🧑‍🧑‍🧒 Family Obesity History", ["Yes", "No"])

    st.markdown("##### 🥕 Diet and Lifestyle")
    c4, c5, c6 = st.columns(3)
    with c4:
        vegetable_days = st.slider("🥬 Vegetable Intake Days per Week", 0, 7, 3)
        high_calorie_food = st.selectbox("🍿 High-Calorie Food", ["Yes", "No"])
        main_meals = st.slider("🍚 Daily Main Meals", 1, 5, 3)
    with c5:
        snack_frequency = st.selectbox("🍰 Snack Frequency", ["Always", "Frequently", "Occasionally"])
        sugary_drinks = st.selectbox("🥤 Sugary Drinks", ["Yes", "No"])
        water_intake = st.slider("💧 Daily Water Intake (L)", 0.0, 5.0, 2.0, 0.1)
    with c6:
        alcohol_frequency = st.selectbox("🍷 Alcohol Frequency", ["None", "Occasionally", "Frequently"])

    c7, c8 = st.columns(2)
    with c7:
        exercise_days = st.slider("🏋️ Exercise Days per Week", 0, 7, 2)
        screen_time = st.slider("📱 Daily Screen Time (hours)", 0, 24, 3)
    with c8:
        transportation = st.selectbox("🚗 Transportation Mode", ["Car", "Bicycle", "Motorcycle", "Public Transport", "Walking"])
        smoke = st.selectbox("🚬 Smoking", ["Yes", "No"])

    st.markdown("##### 🔛 Plan Start Date")
    start_choice = st.radio("7-Day Plan Starts:", ["Today", "Tomorrow"], horizontal=True)
    user = {
        "gender": gender, "age": age, "height": height, "weight": weight,
        "family_history": family_history, "high_calorie_food": high_calorie_food,
        "vegetable_days": vegetable_days, "main_meals": main_meals,
        "snack_frequency": snack_frequency, "smoke": smoke, "water_intake": water_intake,
        "sugary_drinks": sugary_drinks, "exercise_days": exercise_days, "screen_time": screen_time,
        "alcohol_frequency": alcohol_frequency, "transportation": transportation,
        "start_choice": start_choice
    }

    submitted = st.form_submit_button("🚀 Generate Meal Plan")

# ---------- Handle Form Submission and BMI Suggestions ----------
if submitted:
    with st.spinner("Generating your meal plan..."):
        df = build_recipes(user, preferences, cuisine if cuisine != "Any" else None, 
                         difficulty if difficulty != "Any" else None, exclude_ingredients)
        # Calculate BMI and display health suggestions
        bmi = user["weight"] / (user["height"] ** 2)
        bmi_category = (
            "Underweight" if bmi < 18.5 else
            "Normal" if 18.5 <= bmi < 25 else
            "Overweight" if 25 <= bmi < 30 else
            "Obese"
        )
        st.markdown(f"**Your BMI**: {bmi:.1f} ({bmi_category})")
        if bmi_category == "Overweight" or bmi_category == "Obese":
            st.info("Consider choosing low-calorie, high-protein meals and increasing weekly exercise frequency.")
        elif bmi_category == "Underweight":
            st.info("Consider choosing high-calorie, high-protein meals to increase nutrient intake.")
        elif bmi_category == "Normal":
            st.info("Your weight is within a healthy range. Maintain a balanced diet and moderate exercise!")
    st.balloons()
    st.session_state["full_df"] = df

# ---------- Display Meal Plan, Nutrition Summary, and Shopping List ----------
if "full_df" in st.session_state:
    df = st.session_state["full_df"]
    
    # Display Meal Plan
    st.markdown('<div class="title">📅 Your 7-Day Meal Plan</div>', unsafe_allow_html=True)
    for day in df["day"].unique():
        if f"show_{day}" not in st.session_state:
            st.session_state[f"show_{day}"] = True
        
        if st.button(f"📆 {day}", key=f"toggle_{day}", help="Click to show/hide meal plan"):
            st.session_state[f"show_{day}"] = not st.session_state[f"show_{day}"]
        
        if st.session_state[f"show_{day}"]:
            day_df = df[df["day"] == day].reset_index(drop=True)
            st.markdown(f'<div id="{day}" class="meal-container">', unsafe_allow_html=True)
            for idx, row in day_df.iterrows():
                dish_key = row["dish"].lower().replace(" ", "_")
                img_path = f"images/{dish_key}.jpg"
                img_file = img_path if os.path.exists(img_path) else "images/placeholder.jpg"
                # Add ID to each meal card for scrolling
                st.markdown(f'<div id="{row["dish"]}" class="meal-card">', unsafe_allow_html=True)
                st.image(img_file, width=img_size)
                meal_emoji = "🥐" if row["meal"] == "Breakfast" else "🍲" if row["meal"] == "Lunch" else "🍽️"
                st.markdown(f'<div class="meal-content">', unsafe_allow_html=True)
                st.markdown(f'<div class="meal-title">{meal_emoji} {row["meal"]}: {row["dish"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meal-calories">{int(row["calories"])} kcal</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meal-details"><strong>Nutrition:</strong> Carbohydrates {row["carbohydrates"]}g, Protein {row["protein"]}g, Fat {row["fat"]}g</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meal-details"><strong>Ingredients:</strong> {row["ingredients"]}<br><strong>Steps:</strong> {row["steps"]}</div>', unsafe_allow_html=True)
                # Favorite/Unfavorite Buttons
                if row["dish"] in st.session_state["favorites"]:
                    if st.button("Remove from Favorites", key=f"unfavorite_{day}_{row['meal']}_{row['dish']}", help="Remove dish from favorites"):
                        st.session_state["favorites"].remove(row["dish"])
                        st.success(f"Removed from favorites: {row['dish']}")
                        st.rerun()
                else:
                    if st.button("Add to Favorites", key=f"favorite_{day}_{row['meal']}_{row['dish']}", help="Add dish to favorites"):
                        st.session_state["favorites"].append(row["dish"])
                        st.success(f"Added to favorites: {row['dish']}")
                        st.rerun()
                # Refresh Dish Button
                if st.button("Replace Dish", key=f"refresh_{day}_{row['meal']}_{row['dish']}", help="Select a different dish", type="primary"):
                    meal_data = RECIPE_DB[row["meal"]]
                    available_dishes = list(meal_data.keys())
                    if preferences or cuisine or difficulty or exclude_ingredients:
                        available_dishes = [
                            dish for dish in available_dishes
                            if (not preferences or any(tag in meal_data[dish]["tags"] for tag in preferences)) and
                            (not cuisine or ("Cuisine" in meal_data[dish] and meal_data[dish]["Cuisine"] == cuisine)) and
                            (not difficulty or ("Difficulty" in meal_data[dish] and meal_data[dish]["Difficulty"] == difficulty)) and
                            (not exclude_ingredients or not any(ing.lower() in meal_data[dish]["ingredients"].lower() for ing in exclude_ingredients))
                        ]
                    if not available_dishes:
                        available_dishes = list(meal_data.keys())
                    new_dish = random.choice(available_dishes)
                    df.loc[(df["day"] == day) & (df["meal"] == row["meal"]), "dish"] = new_dish
                    df.loc[(df["day"] == day) & (df["meal"] == row["meal"]), "calories"] = meal_data[new_dish]["calories"]
                    df.loc[(df["day"] == day) & (df["meal"] == row["meal"]), "carbohydrates"] = meal_data[new_dish]["carbohydrates"]
                    df.loc[(df["day"] == day) & (df["meal"] == row["meal"]), "protein"] = meal_data[new_dish]["protein"]
                    df.loc[(df["day"] == day) & (df["meal"] == row["meal"]), "fat"] = meal_data[new_dish]["fat"]
                    df.loc[(df["day"] == day) & (df["meal"] == row["meal"]), "ingredients"] = meal_data[new_dish]["ingredients"]
                    df.loc[(df["day"] == day) & (df["meal"] == row["meal"]), "steps"] = meal_data[new_dish]["steps"]
                    st.session_state["full_df"] = df
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Auto-scroll to favorited dish
            if "scroll_to_dish" in st.session_state and st.session_state["scroll_to_dish"] in day_df["dish"].values:
                st.markdown(
                    f"""
                    <script>
                        document.getElementById("{st.session_state['scroll_to_dish']}").scrollIntoView({{behavior: 'smooth'}});
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                del st.session_state["scroll_to_dish"]

    # ---------- Export Meal Plan ----------
    st.markdown('<div class="download-section">📥 <a href="data:text/csv;charset=utf-8,' + df.to_csv(index=False).replace("\n", "%0A") + '" download="7day_menu.csv">Export Weekly Meal Plan</a></div>', unsafe_allow_html=True)

    # ---------- Shopping List ----------
    st.markdown('<div class="title">🛒 Shopping List</div>', unsafe_allow_html=True)
    ingredients_list = []
    for ingredients in df["ingredients"]:
        ingredients_list.extend([item.strip() for item in ingredients.split(",")])
    shopping_list = sorted(list(set(ingredients_list)))
    st.write("Ingredients needed for the 7-day meal plan:")
    st.write(", ".join(shopping_list))
    shopping_df = pd.DataFrame(shopping_list, columns=["Ingredients"])
    st.markdown(
        '<div class="download-section">📥 <a href="data:text/csv;charset=utf-8,' + 
        shopping_df.to_csv(index=False).replace("\n", "%0A") + 
        '" download="shopping_list.csv">Export Shopping List</a></div>', 
        unsafe_allow_html=True
    )

    # ---------- Daily Nutrition Summary and Comparison ----------
    st.markdown('<div class="title">📊 Daily Nutrition Summary</div>', unsafe_allow_html=True)
    with st.expander("🤔The meaning of each indicator", expanded=False):
        st.write("""
        - **Calories (kcal)**: Total daily calorie intake in kilocalories.
        - **Calories Difference (kcal)**: Difference between actual and target calorie intake (positive = excess, negative = deficit).
        - **Carbohydrates (g)**: Total daily carbohydrate intake in grams.
        - **Carbohydrates Difference (g)**: Difference between actual and target carbohydrate intake (positive = excess, negative = deficit).
        - **Protein (g)**: Total daily protein intake in grams.
        - **Protein Difference (g)**: Difference between actual and target protein intake (positive = excess, negative = deficit).
        - **Fat (g)**: Total daily fat intake in grams.
        - **Fat Difference (g)**: Difference between actual and target fat intake (positive = excess, negative = deficit).
        """)
    daily = df.groupby("day")[["calories", "carbohydrates", "protein", "fat"]].sum().round(1).reset_index()
    daily["day"] = pd.Categorical(daily["day"], categories=df["day"].cat.categories, ordered=True)
    daily = daily.sort_values("day")
    daily["calories_diff"] = daily["calories"] - target_calories
    daily["protein_diff"] = daily["protein"] - target_protein
    daily["carbohydrates_diff"] = daily["carbohydrates"] - target_carbohydrates
    daily["fat_diff"] = daily["fat"] - target_fat
    st.dataframe(
        daily.set_index("day").rename(columns={
            "calories": "Calories (kcal)",
            "calories_diff": "Calories Difference (kcal)",
            "carbohydrates": "Carbohydrates (g)",
            "carbohydrates_diff": "Carbohydrates Difference (g)",
            "protein": "Protein (g)",
            "protein_diff": "Protein Difference (g)",
            "fat": "Fat (g)",
            "fat_diff": "Fat Difference (g)"
        }),
        column_config={
            "Calories (kcal)": st.column_config.NumberColumn(
                help="Total daily calorie intake"),
            "Calories Difference (kcal)": st.column_config.NumberColumn(
                help="Difference between actual and target calorie intake (positive = excess, negative = deficit)"),
            "Carbohydrates (g)": st.column_config.NumberColumn(
                help="Total daily carbohydrate intake"),
            "Carbohydrates Difference (g)": st.column_config.NumberColumn(
                help="Difference between actual and target carbohydrate intake (positive = excess, negative = deficit)"),
            "Protein (g)": st.column_config.NumberColumn(
                help="Total daily protein intake"),
            "Protein Difference (g)": st.column_config.NumberColumn(
                help="Difference between actual and target protein intake (positive = excess, negative = deficit)"),
            "Fat (g)": st.column_config.NumberColumn(
                help="Total daily fat intake"),
            "Fat Difference (g)": st.column_config.NumberColumn(
                help="Difference between actual and target fat intake (positive = excess, negative = deficit)")
        },
        use_container_width=True
    )

    # ---------- Nutrition Data Visualization (Supports Bar, Line, Area Charts) ----------
    st.markdown('<div class="title">📈 Nutrition Trend Chart</div>', unsafe_allow_html=True)
    normalize_data = st.checkbox("Normalize Display (Relative to Target)", value=False, help="Normalize nutrient values to percentages of target values for comparison")
    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Area Chart"], help="Choose your preferred visualization type")
    
    # Data normalization (optional)
    if normalize_data:
        daily_normalized = daily.copy()
        daily_normalized["calories"] = (daily["calories"] / target_calories) * 100
        daily_normalized["protein"] = (daily["protein"] / target_protein) * 100
        daily_normalized["carbohydrates"] = (daily["carbohydrates"] / target_carbohydrates) * 100
        daily_normalized["fat"] = (daily["fat"] / target_fat) * 100
        yaxis_title = "Intake (% of Target)"
        hovertemplate_calories = "%{y:.1f}%"
        hovertemplate_nutrient = "%{y:.1f}%"
    else:
        daily_normalized = daily
        yaxis_title = "Intake"
        hovertemplate_calories = "%{y:.1f} kcal"
        hovertemplate_nutrient = "%{y:.1f} g"

    # Validate data to ensure numeric values
    for col in ["calories", "protein", "carbohydrates", "fat"]:
        daily_normalized[col] = pd.to_numeric(daily_normalized[col], errors="coerce").fillna(0)

    fig = go.Figure()
    trace_type = go.Bar if chart_type == "Bar Chart" else go.Scatter
    fill_mode = 'tozeroy' if chart_type == "Area Chart" else None
    
    if normalize_data:
        # Normalized data uses a single y-axis
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["calories"], name="Calories (kcal)",
            marker_color="rgba(34, 197, 94, 0.7)",
            hovertemplate=hovertemplate_calories,
            **({"fill": fill_mode, "mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["protein"], name="Protein (g)",
            marker_color="rgba(59, 130, 246, 0.7)",
            hovertemplate=hovertemplate_nutrient,
            **({"fill": fill_mode, "mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["carbohydrates"], name="Carbohydrates (g)",
            marker_color="rgba(249, 168, 37, 0.7)",
            hovertemplate=hovertemplate_nutrient,
            **({"fill": fill_mode, "mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["fat"], name="Fat (g)",
            marker_color="rgba(239, 68, 68, 0.7)",
            hovertemplate=hovertemplate_nutrient,
            **({"fill": fill_mode, "mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.update_layout(
            title="Daily Nutrition Intake (Normalized)",
            xaxis_title="Date",
            yaxis_title=yaxis_title,
            barmode="group" if chart_type == "Bar Chart" else "overlay",
            template="plotly_white",
            height=400,
            width=850,
            margin=dict(t=80, b=50, l=50, r=120),
            legend=dict(orientation="h", yanchor="top", y=1.2, xanchor="center", x=0.5),
            hovermode="x unified"
        )
    else:
        # Non-normalized data uses dual y-axes
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["calories"], name="Calories (kcal)",
            marker_color="rgba(34, 197, 94, 0.7)",
            hovertemplate=hovertemplate_calories,
            yaxis="y1",
            **({"mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["protein"], name="Protein (g)",
            marker_color="rgba(59, 130, 246, 0.7)",
            hovertemplate=hovertemplate_nutrient,
            yaxis="y2",
            **({"fill": fill_mode, "mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["carbohydrates"], name="Carbohydrates (g)",
            marker_color="rgba(249, 168, 37, 0.7)",
            hovertemplate=hovertemplate_nutrient,
            yaxis="y2",
            **({"fill": fill_mode, "mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.add_trace(trace_type(
            x=daily["day"], y=daily_normalized["fat"], name="Fat (g)",
            marker_color="rgba(239, 68, 68, 0.7)",
            hovertemplate=hovertemplate_nutrient,
            yaxis="y2",
            **({"fill": fill_mode, "mode": "lines+markers"} if trace_type == go.Scatter else {})
        ))
        fig.update_layout(
            title="Daily Nutrition Intake",
            xaxis_title="Date",
            yaxis=dict(
                title="Calories (kcal)",
                side="left",
                range=[0, daily["calories"].max() * 1.1]
            ),
            yaxis2=dict(
                title="Macronutrients (g)",
                overlaying="y",
                side="right",
                range=[0, max(daily["protein"].max(), daily["carbohydrates"].max(), daily["fat"].max()) * 1.1]
            ),
            barmode="group" if chart_type == "Bar Chart" else "overlay",
            template="plotly_white",
            height=400,
            width=850,
            margin=dict(t=80, b=50, l=50, r=120),
            legend=dict(orientation="h", yanchor="top", y=1.2, xanchor="center", x=0.5),
            hovermode="x unified"
        )
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})