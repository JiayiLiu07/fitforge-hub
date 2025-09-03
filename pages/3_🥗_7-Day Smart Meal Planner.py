import pandas as pd
import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
from datetime import datetime, timedelta
import plotly.graph_objects as go
import json
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import requests
import re
import random

# Check for API Key from main page
if not st.session_state.get("api_key"):
    st.markdown(
        """
        <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
            🥗 7-Day Smart Meal Planner
        </h1>
        <p style='text-align:center; font-size:1.1rem; color:#6c757d;'>
        Customize your weekly meal plan based on your preferences and personal information!
        </p>
        """,
        unsafe_allow_html=True
    )
    st.warning("⚠️ Please go to the sidebar and enter a valid API key in FitForge_Hub🚀 page")
    st.stop()

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Streamlit configuration
st.set_page_config(page_title="7-Day Smart Meal Planner", page_icon="🥗", layout="wide")

# Custom CSS for Tailwind-inspired styling with uniform card height and horizontal buttons
st.markdown("""
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .stButton>button {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        border: 1px solid #d1d5db !important;
        font-weight: 600;
        transition: background-color 0.2s;
        font-size: 0.85rem;
    }
    .stButton>button:hover { background-color: #f3f4f6 !important; }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select, .stSlider>div>div, .stDateInput>div>input {
        border: 1px solid #d1d5db;
        border-radius: 0.375rem;
        padding: 0.5rem;
    }
    .stRadio>div { border: none; padding: 0.5rem; }
    .stMarkdown h1 { color: #1f2937; font-size: 2rem; font-weight: 700; }
    .stMarkdown h2 { color: #374151; font-size: 1.5rem; font-weight: 600; }
    .title-container { text-align: center; }
    .main-title { font-size: 2.8rem; color: #1f2937; font-weight: 700; }
    .subtitle { font-size: 1.5rem; color: #6b7280; font-weight: 600; text-align: center; }
    .divider {
        border: 0;
        height: 1px;
        background-color: #d1d5db;
        margin: 1rem 0;
    }
    .title {
        color: #374151;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease-in;
    }
    .normal { background-color: #d1fae5; border-color: #10b981; }
    .underweight { background-color: #fef9c3; border-color: #facc15; }
    .overweight { background-color: #fed7aa; border-color: #f97316; }
    .obesity { background-color: #fee2e2; border-color: #ef4444; }
    .emoji-pulse {
        display: inline-block;
        animation: pulse 1.5s infinite;
        margin-left: 0.5rem;
    }
    .result-text {
        display: flex;
        align-items: center;
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f2937;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .progress-bar {
        background-color: #e5e7eb;
        border-radius: 0.375rem;
        height: 1rem;
        overflow: hidden;
    }
    .progress-fill {
        background-color: #3b82f6;
        height: 100%;
        transition: width 0.5s ease-in-out;
    }
    .download-section {
        margin-top: 1rem;
        font-size: 1rem;
    }
    .meal-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        height: 400px;
        overflow: hidden;
    }
    .meal-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    .meal-calories {
        font-size: 0.9rem;
        color: #10b981;
        margin-bottom: 0.5rem;
    }
    .meal-content {
        display: flex;
        flex-direction: column;
        flex: 1;
        overflow: hidden;
    }
    .meal-details {
        font-size: 0.85rem;
        color: #374151;
        overflow-y: auto;
        flex: 1;
        margin-bottom: 0.5rem;
    }
    .button-container {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        gap: 0.5rem;
        margin-top: auto;
        justify-content: space-between;
        align-items: center;
    }
    .favorite-button {
        background-color: #ffffff !important;
        border: 1px solid #10b981 !important;
        border-radius: 0.375rem;
        padding: 0.5rem;
        flex: 1;
        text-align: center;
        transition: background-color 0.2s;
        color: #065f46 !important;
        font-size: 0.85rem;
        min-width: 80px;
        max-width: 120px;
    }
    .favorite-button:hover {
        background-color: #f3f4f6 !important;
    }
    .favorite-button.favorited {
        background-color: #ffffff !important;
        border: 1px solid #ef4444 !important;
        color: #991b1b !important;
    }
    .favorite-button.favorited:hover {
        background-color: #f3f4f6 !important;
    }
    .favorite-nav-button {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 0.375rem;
        padding: 0.5rem;
        width: 100%;
        text-align: center;
        transition: background-color 0.2s;
        color: #1f2937 !important;
    }
    .favorite-nav-button:hover {
        background-color: #f3f4f6 !important;
    }
    .change-button {
        background-color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 0.375rem;
        padding: 0.5rem;
        flex: 1;
        text-align: center;
        transition: background-color 0.2s;
        color: #1f2937 !important;
        font-size: 0.85rem;
        min-width: 80px;
        max-width: 120px;
    }
    .change-button:hover {
        background-color: #f3f4f6 !important;
    }
    .prediction-link {
        background-color: #e0f2fe;
        border-radius: 0.375rem;
        padding: 0.25rem 0.5rem;
        transition: transform 0.2s ease-in-out;
        display: inline-block;
    }
    .prediction-link:hover {
        transform: scale(1.02);
    }
    .tip-box {
        background-color: #e0f2fe;
        border: 1px solid #3b82f6;
        border-radius: 0.375rem;
        padding: 0.5rem;
        font-size: 0.9rem;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    @media (max-width: 640px) {
        .result-text { font-size: 1rem; }
        .meal-card { height: 450px; }
        .button-container { flex-direction: row; flex-wrap: nowrap; gap: 0.25rem; }
        .stButton>button, .favorite-button, .change-button { font-size: 0.8rem; padding: 0.4rem; min-width: 70px; max-width: 100px; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Add title and subtitle
st.markdown(
    """
    <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
        🥗 7-Day Smart Meal Planner
    </h1>
    <p class='subtitle' style='margin-bottom: 1rem;'>Customize your weekly meal plan based on your preferences and personal information!</p>
    """,
    unsafe_allow_html=True,
)

# WHO BMI ranges
bmi_ranges = pd.DataFrame({
    'BMI Range': ['< 18.5', '18.5 - 24.9', '25.0 - 27.4', '27.5 - 29.9', '30.0 - 34.9', '35.0 - 39.9', '>= 40.0'],
    'Obesity Level': ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I', 'Overweight_Level_II', 
                      'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']
})

# Extended Fallback image mapping for dishes
FALLBACK_IMAGES = {
    "Oats & Berries Bowl": "https://img2.baidu.com/it/u=4230460056,2597757457&fm=253&fmt=auto&app=138&f=JPEG?w=686&h=500.jpg",
    "Egg & Avocado Toast": "https://www.jessicagavin.com/wp-content/uploads/2020/07/avocado-toast-20.jpg",
    "Greek Yogurt Parfait": "https://myeverydaytable.com/wp-content/uploads/YogurtParfait-7.jpg",
    "Grilled Chicken Salad": "https://img0.baidu.com/it/u=3785619211,3605961101&fm=253&fmt=auto&app=138&f=JPEG?w=681&h=500.jpg",
    "Tofu Stir-fry": "https://img2.baidu.com/it/u=1373407432,4063135306&fm=253&fmt=auto&app=120&f=JPEG?w=872&h=500.jpg",
    "Quinoa Salad": "https://img2.baidu.com/it/u=2977731160,2906746483&fm=253&fmt=auto&app=138&f=JPEG?w=371&h=247.jpg",
    "Baked Cod & Veg": "https://img0.baidu.com/it/u=3855779815,2942985540&fm=253&fmt=auto&app=138&f=JPEG?w=515&h=500.jpg",
    "Lentil Curry": "https://img1.baidu.com/it/u=1085263699,3156093026&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=747.jpg",
    "Grilled Salmon": "https://img0.baidu.com/it/u=1614082101,2058372571&fm=253&fmt=auto&app=138&f=JPEG?w=681&h=500.jpg",
    "Greek Yogurt with Berries": "https://img0.baidu.com/it/u=3072303642,3292055252&fm=253&fmt=auto&app=138&f=JPEG?w=372&h=247.jpg",
    "Grilled Chicken Quinoa Bowl": "https://gips2.baidu.com/it/u=3583929422,3202639676&fm=3074&app=3074&f=JPEG?w=1857&h=1336&type=normal&func=T.jpg",
    "Baked Salmon with Sweet Potato": "https://img2.baidu.com/it/u=3918213213,723548576&fm=253&fmt=auto&app=138&f=JPEG?w=428&h=285.jpg",
    "Veggie Omelette": "https://qcloud.dpfile.com/pc/XPfoOHVXay6x3sIv9HEbo97coXoyHGbagwab2BpeNNqddsqsSsc-Nlpxeueo9Ou6.jpg",
    "Lentil Salad with Tuna": "https://img1.baidu.com/it/u=136919957,3673211005&fm=253&fmt=auto&app=138&f=JPEG?w=776&h=500.jpg",
    "Turkey Stir Fry": "https://img1.baidu.com/it/u=2339721432,454675603&fm=253&fmt=auto&app=138&f=JPEG?w=667&h=500.jpg",
    "Smoothie Bowl": "https://img0.baidu.com/it/u=1120659700,3981340333&fm=253&app=138&f=JPEG?w=500&h=652.jpg",
    "Whole Wheat Turkey Wrap": "https://img0.baidu.com/it/u=2225449939,3281285977&fm=253&fmt=auto&app=138&f=JPEG?w=671&h=500.jpg",
    "Zucchini Noodles": "https://img1.baidu.com/it/u=68976516,2487486160&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=616.jpg",
    "Chickpea and Spinach Curry": "https://img2.baidu.com/it/u=4028398599,4175896441&fm=253&fmt=auto?w=1200&h=800.jpg",
    "Stuffed Bell Peppers": "https://img0.baidu.com/it/u=2880936394,2877277857&fm=253&fmt=auto&app=138&f=JPEG?w=455&h=304.jpg",
    "Cottage Cheese with Fruit": "https://img1.baidu.com/it/u=1940315113,1076483978&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=333",
    "Tuna and Bean Salad": "https://img1.baidu.com/it/u=3080151194,525246636&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500.jpg",
    "Grilled Chicken with Veggies": "https://img1.baidu.com/it/u=3948725571,3102824782&fm=253&fmt=auto&app=138&f=JPEG?w=514&h=500.jpg",
    "Overnight Oats": "https://img2.baidu.com/it/u=1956992169,4136788662&fm=253&fmt=auto&app=138&f=JPEG?w=509&h=500.jpg",
    "Quinoa and Chickpea Salad": "https://img0.baidu.com/it/u=3571550826,1410301313&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=652.jpg",
    "Shrimp Stir Fry": "https://img2.baidu.com/it/u=23070658,1949138698&fm=253&fmt=auto&app=120&f=JPEG?w=500&h=667.jpg",
    "Egg and Veggie Scramble": "https://pic.rmb.bdstatic.com/bjh/240118/c8c52c1409980a7d278ab32ec8b58c5b1291.jpeg.jpg",
    "Lentil Soup": "https://img1.baidu.com/it/u=841389781,2107563934&fm=253&fmt=auto&app=120&f=JPEG?w=682&h=1023.jpg",
    "Baked Chicken Thighs": "https://img1.baidu.com/it/u=3108058182,712928160&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=667.jpg",
    "Mediterranean Chickpea Bowl": "https://img2.baidu.com/it/u=2237125653,3962951722&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=664.jpg",
    "Vegetable Sushi Roll": "https://qcloud.dpfile.com/pc/yhO7fjhU5yUP3ipJPfpLrXqFAIfDHEmTusH3fq7szzVwSlNDOb86AJm5jcwCW_og.jpg",
    "Thai Green Curry": "https://img2.baidu.com/it/u=3279478426,2180878125&fm=253&fmt=auto&app=138&f=JPEG?w=667&h=500.jpg",
    "Baked Tofu with Veggies": "https://img2.baidu.com/it/u=50065624,2459776987&fm=253&fmt=auto&app=138&f=JPEG?w=668&h=500.jpg",
    "Falafel Wrap": "https://img2.baidu.com/it/u=429177048,4235961126&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=657.jpg",
    "Miso Soup with Tofu": "https://img0.baidu.com/it/u=215810027,2181767460&fm=253&fmt=auto&app=138&f=JPEG?w=750&h=500.jpg",
    "Spaghetti Squash": "https://qcloud.dpfile.com/pc/NUovHdke-H0NF5qK7cU1KNNLgLIGUkWxQg6oQGWBrw36yiiYeocFIjl9YnOm2Umq.jpg",
    "Fallback Breakfast Dish": "https://img0.baidu.com/it/u=1642982904,40582365&fm=253&fmt=auto&app=138&f=JPEG?w=800&h=1067.jpg",
    "Fallback Lunch Dish": "https://img2.baidu.com/it/u=255562951,3727218015&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=375.jpg",
    "Fallback Dinner Dish": "https://img1.baidu.com/it/u=245802027,453897840&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=666.jpg"
}

# Fallback Recipe Database
RECIPE_DB = {
    "Breakfast": {
        "Oats & Berries Bowl": {
            "calories": 320, "carbohydrates": 45, "protein": 12, "fat": 8,
            "ingredients": "Oats, mixed berries, almond milk, honey",
            "steps": "Mix all ingredients, refrigerate overnight. Easy.",
            "image_url": FALLBACK_IMAGES["Oats & Berries Bowl"]
        },
        "Egg & Avocado Toast": {
            "calories": 380, "carbohydrates": 30, "protein": 18, "fat": 22,
            "ingredients": "Whole-wheat toast, eggs, avocado, lemon juice",
            "steps": "Toast bread, fry eggs, mash avocado with lemon, assemble. Easy.",
            "image_url": FALLBACK_IMAGES["Egg & Avocado Toast"]
        },
        "Greek Yogurt Parfait": {
            "calories": 300, "carbohydrates": 40, "protein": 15, "fat": 10,
            "ingredients": "Greek yogurt, granola, mixed fruits, chia seeds",
            "steps": "Layer yogurt, granola, and fruits in a glass. Easy.",
            "image_url": FALLBACK_IMAGES["Greek Yogurt Parfait"]
        },
        "Vegetable Sushi Roll": {
            "calories": 280, "carbohydrates": 35, "protein": 8, "fat": 10,
            "ingredients": "Sushi rice, nori, cucumber, avocado, carrot",
            "steps": "Spread rice on nori, add veggies, roll tightly, slice. Medium.",
            "image_url": FALLBACK_IMAGES["Vegetable Sushi Roll"]
        },
        "Smoothie Bowl": {
            "calories": 340, "carbohydrates": 50, "protein": 10, "fat": 12,
            "ingredients": "Banana, spinach, almond milk, protein powder, chia seeds",
            "steps": "Blend ingredients, pour into bowl, top with nuts. Easy.",
            "image_url": FALLBACK_IMAGES["Smoothie Bowl"]
        },
        "Veggie Omelette": {
            "calories": 320, "carbohydrates": 15, "protein": 20, "fat": 18,
            "ingredients": "Eggs, spinach, bell peppers, onion, cheese",
            "steps": "Whisk eggs, cook with veggies, add cheese, fold. Medium.",
            "image_url": FALLBACK_IMAGES["Veggie Omelette"]
        },
        "Overnight Oats": {
            "calories": 350, "carbohydrates": 40, "protein": 15, "fat": 12,
            "ingredients": "Oats, peanut butter, almond milk, banana",
            "steps": "Mix oats, peanut butter, milk, top with banana, chill overnight. Easy.",
            "image_url": FALLBACK_IMAGES["Overnight Oats"]
        },
    },
    "Lunch": {
        "Grilled Chicken Salad": {
            "calories": 420, "carbohydrates": 20, "protein": 35, "fat": 22,
            "ingredients": "Chicken breast, lettuce, tomato, cucumber, olive oil",
            "steps": "Grill chicken, chop veggies, toss with olive oil dressing. Medium.",
            "image_url": FALLBACK_IMAGES["Grilled Chicken Salad"]
        },
        "Tofu Stir-fry": {
            "calories": 390, "carbohydrates": 35, "protein": 20, "fat": 18,
            "ingredients": "Tofu, broccoli, bell pepper, soy sauce, sesame oil",
            "steps": "Stir-fry tofu and veggies with soy sauce and sesame oil. Medium.",
            "image_url": FALLBACK_IMAGES["Tofu Stir-fry"]
        },
        "Quinoa Salad": {
            "calories": 360, "carbohydrates": 40, "protein": 12, "fat": 15,
            "ingredients": "Quinoa, cucumber, tomato, feta, olive oil",
            "steps": "Cook quinoa, mix with veggies, add feta and dressing. Easy.",
            "image_url": FALLBACK_IMAGES["Quinoa Salad"]
        },
        "Lentil Salad with Tuna": {
            "calories": 400, "carbohydrates": 30, "protein": 28, "fat": 15,
            "ingredients": "Lentils, tuna, red onion, parsley, lemon juice",
            "steps": "Cook lentils, mix with tuna and veggies, dress with lemon. Easy.",
            "image_url": FALLBACK_IMAGES["Lentil Salad with Tuna"]
        },
        "Falafel Wrap": {
            "calories": 380, "carbohydrates": 45, "protein": 12, "fat": 14,
            "ingredients": "Falafel, pita bread, lettuce, tahini, cucumber",
            "steps": "Fry falafel, assemble in pita with veggies and tahini. Medium.",
            "image_url": FALLBACK_IMAGES["Falafel Wrap"]
        },
        "Mediterranean Chickpea Bowl": {
            "calories": 370, "carbohydrates": 38, "protein": 14, "fat": 16,
            "ingredients": "Chickpeas, cucumber, olives, feta, hummus",
            "steps": "Mix chickpeas with veggies, top with hummus and feta. Easy.",
            "image_url": FALLBACK_IMAGES["Mediterranean Chickpea Bowl"]
        },
        "Tuna and Bean Salad": {
            "calories": 390, "carbohydrates": 25, "protein": 30, "fat": 15,
            "ingredients": "Tuna, white beans, red onion, parsley, olive oil",
            "steps": "Mix tuna and beans with veggies, dress with olive oil. Easy.",
            "image_url": FALLBACK_IMAGES["Tuna and Bean Salad"]
        },
    },
    "Dinner": {
        "Baked Cod & Veg": {
            "calories": 380, "carbohydrates": 25, "protein": 32, "fat": 14,
            "ingredients": "Cod, asparagus, garlic, lemon, olive oil",
            "steps": "Bake cod and veggies at 200°C for 15 min with lemon and oil. Medium.",
            "image_url": FALLBACK_IMAGES["Baked Cod & Veg"]
        },
        "Lentil Curry": {
            "calories": 410, "carbohydrates": 45, "protein": 20, "fat": 12,
            "ingredients": "Lentils, coconut milk, curry paste, onion, spinach",
            "steps": "Simmer lentils with coconut milk and spices for 20 min. Medium.",
            "image_url": FALLBACK_IMAGES["Lentil Curry"]
        },
        "Grilled Salmon": {
            "calories": 400, "carbohydrates": 15, "protein": 30, "fat": 20,
            "ingredients": "Salmon, zucchini, lemon, dill, olive oil",
            "steps": "Grill salmon, roast zucchini, season with lemon and dill. Medium.",
            "image_url": FALLBACK_IMAGES["Grilled Salmon"]
        },
        "Chickpea and Spinach Curry": {
            "calories": 390, "carbohydrates": 40, "protein": 15, "fat": 14,
            "ingredients": "Chickpeas, spinach, coconut milk, curry powder",
            "steps": "Cook chickpeas with spinach and curry in coconut milk. Medium.",
            "image_url": FALLBACK_IMAGES["Chickpea and Spinach Curry"]
        },
        "Stuffed Bell Peppers": {
            "calories": 420, "carbohydrates": 35, "protein": 18, "fat": 16,
            "ingredients": "Bell peppers, quinoa, black beans, cheese",
            "steps": "Stuff peppers with quinoa and beans, bake with cheese. Hard.",
            "image_url": FALLBACK_IMAGES["Stuffed Bell Peppers"]
        },
        "Thai Green Curry": {
            "calories": 430, "carbohydrates": 30, "protein": 20, "fat": 22,
            "ingredients": "Tofu, green curry paste, coconut milk, eggplant",
            "steps": "Cook tofu with curry paste and coconut milk, add veggies. Hard.",
            "image_url": FALLBACK_IMAGES["Thai Green Curry"]
        },
        "Baked Tofu with Veggies": {
            "calories": 360, "carbohydrates": 25, "protein": 25, "fat": 15,
            "ingredients": "Tofu, broccoli, carrots, soy sauce, sesame seeds",
            "steps": "Marinate tofu, bake with veggies at 200°C for 20 min. Medium.",
            "image_url": FALLBACK_IMAGES["Baked Tofu with Veggies"]
        },
    }
}

# Initialize dish cache
if "dish_cache" not in st.session_state:
    st.session_state["dish_cache"] = {}

# Initialize OpenAI client if API key is available
if "api_key" in st.session_state and st.session_state["api_key"]:
    client = OpenAI(api_key=st.session_state["api_key"])
else:
    client = None

# Function to validate image URL using requests
def validate_image_url(url):
    if not url or not url.startswith("https://"):
        return False
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# Batch validate image URLs
def batch_validate_urls(urls):
    return [validate_image_url(url) for url in urls]

# Function to determine BMI-based obesity level
def get_bmi_obesity_level(bmi):
    for idx, row in bmi_ranges.iterrows():
        if row['BMI Range'].startswith('<'):
            if bmi < float(row['BMI Range'].replace('< ', '')):
                return row['Obesity Level']
        elif row['BMI Range'].startswith('>='):
            if bmi >= float(row['BMI Range'].replace('>= ', '')):
                return row['Obesity Level']
        else:
            low, high = map(float, row['BMI Range'].split(' - '))
            if low <= bmi <= high:
                return row['Obesity Level']
    return 'Unknown'

# Function to analyze lifestyle risk factors
def analyze_risk_factors(input_data):
    risk_factors = [
        {'name': 'Family history of overweight', 'value': input_data['family_history'], 'condition': 'Yes', 'risk': 'High', 'weight': 0.3},
        {'name': 'Frequent high-calorie food', 'value': input_data['high_calorie_food'], 'condition': 'Yes', 'risk': 'High', 'weight': 0.25},
        {'name': 'Vegetable consumption frequency', 'value': input_data['vegetable_days'], 'condition': lambda x: x <= 3, 'risk': 'High (Low intake)', 'weight': 0.2},
        {'name': 'Main meal frequency', 'value': input_data['main_meals'], 'condition': lambda x: x < 2 or x > 4, 'risk': 'Medium', 'weight': 0.1},
        {'name': 'Food consumption between meals', 'value': input_data['snack_frequency'], 'condition': 'Always', 'risk': 'High', 'weight': 0.2},
        {'name': 'Smoking', 'value': input_data['smoke'], 'condition': 'Yes', 'risk': 'Medium', 'weight': 0.1},
        {'name': 'Physical activity frequency', 'value': input_data['exercise_days'], 'condition': lambda x: x <= 2, 'risk': 'High (Insufficient)', 'weight': 0.2},
        {'name': 'High-calorie drink consumption', 'value': input_data['sugary_drinks'], 'condition': 'Yes', 'risk': 'High', 'weight': 0.2},
        {'name': 'Transportation mode', 'value': input_data['transportation'], 'condition': lambda x: x in ['Car', 'Motorcycle'], 'risk': 'Medium', 'weight': 0.1}
    ]
    
    risk_summary = []
    high_risk_count = 0
    medium_risk_count = 0
    total_risk_score = 0.0
    
    for factor in risk_factors:
        if callable(factor['condition']):
            is_risk = factor['condition'](factor['value'])
        else:
            is_risk = factor['value'] == factor['condition']
        
        risk_level = factor['risk'] if is_risk else 'Neutral'
        risk_summary.append({
            'Factor': factor['name'],
            'Value': factor['value'],
            'Risk': risk_level,
            'Weight': factor['weight']
        })
        if is_risk:
            total_risk_score += factor['weight']
            if 'High' in risk_level:
                high_risk_count += 1
            elif 'Medium' in risk_level:
                medium_risk_count += 1
    
    return pd.DataFrame(risk_summary), high_risk_count, medium_risk_count, total_risk_score

# Function to generate a single dish using API or fallback
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type((AuthenticationError, RateLimitError, APIConnectionError)))
def ai_generate_single_dish(obesity_level, user_inputs, preferences, cuisine, difficulty, exclude_ingredients, day, meal):
    if client is None or not st.session_state.get("api_key"):
        # Fallback to RECIPE_DB
        dishes = list(RECIPE_DB[meal].keys())
        filtered_dishes = [dish for dish in dishes if meets_filter_criteria(
            RECIPE_DB[meal][dish], preferences, cuisine, difficulty, exclude_ingredients
        )]
        if not filtered_dishes:
            filtered_dishes = dishes
        dish_name = random.choice(filtered_dishes)
        dish_data = RECIPE_DB[meal][dish_name].copy()
        dish_data["dish"] = dish_name
        dish_data["day"] = day
        dish_data["meal"] = meal
        return dish_data

    prompt = f"""
    Generate a single {meal} dish for a 7-day meal plan tailored to a user with the following profile:
    - Obesity Level: {obesity_level}
    - Gender: {user_inputs['gender']}
    - Age: {user_inputs['age']}
    - Height: {user_inputs['height']} m
    - Weight: {user_inputs['weight']} kg
    - Dietary Preferences: {', '.join(preferences) if preferences else 'None'}
    - Cuisine Type: {cuisine if cuisine != 'Any' else 'Any'}
    - Cooking Difficulty: {difficulty if difficulty != 'Any' else 'Any'}
    - Excluded Ingredients: {', '.join(exclude_ingredients) if exclude_ingredients else 'None'}
    - Day: {day}
    - Target Calories: {user_inputs['target_calories']} kcal (daily total)
    - Target Protein: {user_inputs['target_protein']} g (daily total)
    - Target Carbohydrates: {user_inputs['target_carbohydrates']} g (daily total)
    - Target Fat: {user_inputs['target_fat']} g (daily total)

    Provide the dish in JSON format with the following fields:
    - dish: Name of the dish
    - calories: Estimated calories (kcal)
    - carbohydrates: Estimated carbohydrates (g)
    - protein: Estimated protein (g)
    - fat: Estimated fat (g)
    - ingredients: Comma-separated list of ingredients
    - steps: Cooking instructions with difficulty level (Easy, Medium, Hard)
    - image_url: A valid HTTPS URL for an image of the dish
    Ensure the dish aligns with the user's preferences, cuisine, difficulty, and excludes specified ingredients.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            timeout=120
        )
        dish_data = json.loads(response.choices[0].message.content)
        if not validate_image_url(dish_data.get("image_url")):
            dish_data["image_url"] = FALLBACK_IMAGES.get(dish_data["dish"], FALLBACK_IMAGES[f"Fallback {meal} Dish"])
        dish_data["day"] = day
        dish_data["meal"] = meal
        return dish_data
    except Exception as e:
        logging.error(f"Failed to generate dish via API: {str(e)}. Using fallback.")
        dishes = list(RECIPE_DB[meal].keys())
        filtered_dishes = [dish for dish in dishes if meets_filter_criteria(
            RECIPE_DB[meal][dish], preferences, cuisine, difficulty, exclude_ingredients
        )]
        if not filtered_dishes:
            filtered_dishes = dishes
        dish_name = random.choice(filtered_dishes)
        dish_data = RECIPE_DB[meal][dish_name].copy()
        dish_data["dish"] = dish_name
        dish_data["day"] = day
        dish_data["meal"] = meal
        return dish_data

# Function to generate 7-day meal plan
def ai_generate_7day_plan(obesity_level, user_inputs, preferences, cuisine, difficulty, exclude_ingredients, base_date):
    days = [(base_date + timedelta(days=i)).strftime("%A, %b %d") for i in range(7)]
    meals = ["Breakfast", "Lunch", "Dinner"]
    meal_plan = []

    for day in days:
        for meal in meals:
            cache_key = f"{obesity_level}_{meal}_{cuisine}_{difficulty}_{'_'.join(sorted(preferences))}_{'_'.join(sorted(exclude_ingredients))}_{day}"
            if cache_key in st.session_state["dish_cache"]:
                dish = st.session_state["dish_cache"][cache_key].copy()
                dish["day"] = day
                dish["meal"] = meal
            else:
                dish = ai_generate_single_dish(obesity_level, user_inputs, preferences, cuisine, difficulty, exclude_ingredients, day, meal)
                st.session_state["dish_cache"][cache_key] = dish.copy()
            meal_plan.append(dish)

    df = pd.DataFrame(meal_plan)
    df["day"] = pd.Categorical(df["day"], categories=days, ordered=True)
    df = df.sort_values(["day", "meal"])
    return df

# Function to check if a dish meets filter criteria
def meets_filter_criteria(dish_data, preferences, cuisine, difficulty, exclude_ingredients):
    include_dish = True
    dish_name = dish_data.get("dish", "")
    ingredients = dish_data.get("ingredients", "").lower().split(",")
    
    # Check dietary preferences
    if "Vegetarian" in preferences and any(ing in ["chicken", "salmon", "cod", "tuna", "turkey", "shrimp"] for ing in ingredients):
        include_dish = False
    if "High-Protein" in preferences and dish_data.get("protein", 0) < 15:
        include_dish = False
    if "Low-Carb" in preferences and dish_data.get("carbohydrates", 0) > 30:
        include_dish = False
    if "Gluten-Free" in preferences and any(ing in ["wheat", "bread", "pita"] for ing in ingredients):
        include_dish = False
    
    # Check excluded ingredients
    if any(exclude.lower() in ingredients for exclude in exclude_ingredients):
        include_dish = False
    
    # Check cuisine
    if cuisine != "Any":
        cuisine_keywords = {
            "Asian": ["tofu", "soy sauce", "curry", "sushi", "miso"],
            "Mediterranean": ["feta", "olive oil", "hummus", "quinoa"],
            "American": ["chicken", "salad", "turkey"]
        }
        if not any(keyword in dish_name.lower() or keyword in ingredients for keyword in cuisine_keywords.get(cuisine, [])):
            include_dish = False
    
    # Check difficulty
    if difficulty != "Any" and difficulty.lower() not in dish_data.get("steps", "").lower():
        include_dish = False
    
    return include_dish

# Sidebar Inputs
with st.sidebar:
    st.markdown("### 🍎 Dietary Preferences")
    st.markdown(
        "<div class='tip-box'>💡Tip: To generate a 7-day meal plan faster, it's best to set filter conditions first (such as dietary preferences, cuisine type, cooking difficulty, excluded ingredients, etc.).</div>",
        unsafe_allow_html=True
    )
    preferences = st.multiselect("Dietary Preferences", ["Vegetarian", "High-Protein", "Low-Carb", "Gluten-Free"], default=st.session_state.get("preferences", []))
    cuisine = st.selectbox("Cuisine Type", ["Any", "Asian", "Mediterranean", "American"], index=["Any", "Asian", "Mediterranean", "American"].index(st.session_state.get("cuisine", "Any")))
    difficulty = st.selectbox("Cooking Difficulty", ["Any", "Easy", "Medium", "Hard"], index=["Any", "Easy", "Medium", "Hard"].index(st.session_state.get("difficulty", "Any")))
    exclude_ingredients = st.text_input("🚫 Excluded Ingredients (comma-separated)", value=",".join(st.session_state.get("exclude_ingredients", []))).split(",")
    exclude_ingredients = [x.strip().lower() for x in exclude_ingredients if x.strip()]

    if "full_df" in st.session_state:
        df = st.session_state["full_df"].copy()
        with st.spinner("Applying filters and updating meal plan..."):
            for idx, row in df.iterrows():
                if not meets_filter_criteria(row, preferences, cuisine, difficulty, exclude_ingredients):
                    cache_key = f"{st.session_state.get('obesity_level', 'Normal_Weight')}_{row['meal']}_{cuisine}_{difficulty}_{'_'.join(sorted(preferences))}_{'_'.join(sorted(exclude_ingredients))}_{row['day']}"
                    if cache_key not in st.session_state["dish_cache"]:
                        new_dish = ai_generate_single_dish(
                            st.session_state.get("obesity_level", "Normal_Weight"),
                            st.session_state.get("user_inputs", {}),
                            preferences,
                            cuisine,
                            difficulty,
                            exclude_ingredients,
                            row["day"],
                            row["meal"]
                        )
                        for key, value in new_dish.items():
                            df.loc[idx, key] = value
                    else:
                        new_dish = st.session_state["dish_cache"][cache_key].copy()
                        new_dish["day"] = row["day"]
                        new_dish["meal"] = row["meal"]
                        for key, value in new_dish.items():
                            df.loc[idx, key] = value
            df["day"] = pd.Categorical(df["day"], categories=df["day"].cat.categories, ordered=True)
            df = df.sort_values(["day", "meal"])
            st.session_state["full_df"] = df
            st.session_state["filtered_df"] = df
            st.session_state["preferences"] = preferences
            st.session_state["cuisine"] = cuisine
            st.session_state["difficulty"] = difficulty
            st.session_state["exclude_ingredients"] = exclude_ingredients
            st.success("Meal plan updated with new dishes based on your filters! 🎉")

    st.markdown("### ⭐ Favorites")
    if "favorites" not in st.session_state:
        st.session_state["favorites"] = []
    if st.session_state["favorites"]:
        for dish in st.session_state["favorites"]:
            def set_selected_dish(dish_name):
                st.session_state["selected_dish"] = dish_name
                st.session_state["scroll_to_dish"] = dish_name

            if st.button(dish, key=f"favorite_nav_{dish}", on_click=set_selected_dish, args=(dish,)):
                pass  # Handled by on_click
        if st.button("🗑️ Clear All Favorites", key="clear_favorites"):
            st.session_state["favorites"] = []
            st.rerun()
    else:
        st.info("No favorite dishes yet. Add some from the meal plan! 🥳")

    # Add debug button to clear session state
    if st.button("🛠️ Debug: Clear Session State"):
        st.session_state.clear()
        st.rerun()

# User Input Form with synchronized defaults from FitForge_Hub🚀.py
with st.form("plan_form"):
    st.markdown("##### 🪪 Personal Information")
    c1, c2 = st.columns(2)
    with c1:
        gender = st.selectbox("⚧️ Gender", ["Male", "Female"], index=["Male", "Female"].index(st.session_state.get("gender", "Male")))
        age = st.slider("🎂 Age", 0, 120, value=st.session_state.get("age", 30))
        family_history = st.selectbox("🧑‍🧒 Family History of Obesity", ["Yes", "No"], index=["yes", "no"].index(st.session_state.get("family_history_with_overweight", "No").lower()))
    with c2:
        height = st.slider("📏 Height (meters)", 0.5, 2.5, value=st.session_state.get("height", 1.7) / 100, step=0.01)
        weight = st.slider("⚖️ Weight (kg)", 20.0, 200.0, value=st.session_state.get("weight", 70.0), step=0.1)

    st.markdown("##### 🥕 Diet and Lifestyle")
    c3, c4 = st.columns(2)
    with c3:
        vegetable_days = st.slider("🥬 Vegetable Consumption (days/week)", 0, 7, value=st.session_state.get("fcvc", 3))
        high_calorie_food = st.selectbox("🍿 High-Calorie Food", ["Yes", "No"], index=["yes", "no"].index(st.session_state.get("favc", "No").lower()))
        main_meals = st.slider("🍚 Main Meals per Day", 1, 5, value=st.session_state.get("ncp", 3))
        try:
            snack_frequency = st.selectbox(
                "🍰 Snack Frequency", 
                ["No", "Sometimes", "Frequently", "Always"], 
                index=["no", "sometimes", "frequently", "always"].index(st.session_state.get("caec", "sometimes").lower())
            )
        except ValueError:
            snack_frequency = st.selectbox(
                "🍰 Snack Frequency", 
                ["No", "Sometimes", "Frequently", "Always"], 
                index=1  # Default to "Sometimes"
            )
        sugary_drinks = st.selectbox("🥤 Sugary Drinks", ["Yes", "No"], index=["yes", "no"].index(st.session_state.get("scc", "No").lower()))
        water_intake = st.slider("💧 Daily Water Intake (liters)", 0.0, 5.0, value=st.session_state.get("ch2o", 2.0), step=0.1)
    with c4:
        try:
            alcohol_frequency = st.selectbox(
                "🍷 Alcohol Frequency", 
                ["No", "Sometimes", "Frequently"], 
                index=["no", "sometimes", "frequently"].index(st.session_state.get("calc", "no").lower())
            )
        except ValueError:
            alcohol_frequency = st.selectbox(
                "🍷 Alcohol Frequency", 
                ["No", "Sometimes", "Frequently"], 
                index=0  # Default to "No"
            )
        exercise_days = st.slider("🏋️ Exercise Days per Week", 0, 7, value=st.session_state.get("faf", 2))
        screen_time = st.slider("📱 Daily Screen Time (hours)", 0, 24, value=st.session_state.get("tue", 3))
        try:
            transportation = st.selectbox(
                "🚗 Transportation Mode", 
                ["Car", "Bicycle", "Motorcycle", "Public Transport", "Walking"], 
                index=["Car", "Bicycle", "Motorcycle", "Public Transport", "Walking"].index(st.session_state.get("mtrans", "Public Transport"))
            )
        except ValueError:
            transportation = st.selectbox(
                "🚗 Transportation Mode", 
                ["Car", "Bicycle", "Motorcycle", "Public Transport", "Walking"], 
                index=3  # Default to "Public Transport"
            )
        smoke = st.selectbox("🚬 Smoking", ["Yes", "No"], index=["yes", "no"].index(st.session_state.get("smoke", "No").lower()))

    st.markdown("##### 🔛 Plan Start Date")
    base_date = st.date_input("Select Plan Start Date", min_value=datetime.now().date(), value=datetime.now().date())

    submitted = st.form_submit_button("🚀 Generate AI Meal Plan")

# Predict and Generate Meal Plan
if submitted:
    user_inputs = {
        "gender": gender, 
        "age": age, 
        "height": height, 
        "weight": weight,
        "family_history": family_history, 
        "high_calorie_food": high_calorie_food,
        "vegetable_days": vegetable_days, 
        "main_meals": main_meals,
        "snack_frequency": snack_frequency, 
        "smoke": smoke,
        "water_intake": water_intake, 
        "sugary_drinks": sugary_drinks,
        "exercise_days": exercise_days, 
        "screen_time": screen_time,
        "alcohol_frequency": alcohol_frequency, 
        "transportation": transportation,
        "target_calories": 2000, 
        "target_protein": 50,
        "target_carbohydrates": 200, 
        "target_fat": 70
    }
    # Update session state to sync with FitForge_Hub🚀.py
    st.session_state.update({
        "gender": gender,
        "age": age,
        "height": height * 100,  # Convert meters to cm
        "weight": weight,
        "family_history_with_overweight": family_history.lower(),
        "favc": high_calorie_food.lower(),
        "fcvc": vegetable_days,
        "ncp": main_meals,
        "caec": snack_frequency.lower(),
        "smoke": smoke.lower(),
        "ch2o": water_intake,
        "scc": sugary_drinks.lower(),
        "faf": exercise_days,
        "tue": screen_time,
        "calc": alcohol_frequency.lower(),
        "mtrans": transportation  # Keep as is, no .lower() to match selectbox options
    })
    
    bmi = weight / (height ** 2)
    bmi_percentage = min(bmi / 40 * 100, 100)
    bmi_obesity_level = get_bmi_obesity_level(bmi)
    risk_df, high_risk_count, medium_risk_count, total_risk_score = analyze_risk_factors(user_inputs)
    
    obesity_levels = ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I', 'Overweight_Level_II', 
                      'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']
    current_level_index = obesity_levels.index(bmi_obesity_level) if bmi_obesity_level in obesity_levels else 1
    prediction = bmi_obesity_level
    if bmi_obesity_level == 'Normal_Weight' and total_risk_score >= 0.8 and bmi >= 22.0:
        prediction = 'Overweight_Level_I'
        risk_summary = (
            "Your BMI ({:.1f}) is within the normal weight range, but your risk score ({:.2f}/1.6) indicates significant lifestyle risk factors (e.g., diet, low exercise, family history). "
            "This suggests a potential progression to Overweight Level I within 6-12 months if lifestyle is not improved."
        ).format(bmi, total_risk_score)
    elif total_risk_score >= 0.8 and current_level_index < len(obesity_levels) - 1:
        prediction = obesity_levels[current_level_index + 1]
        risk_summary = (
            "Your BMI ({:.1f}) indicates {}, but a high risk score ({:.2f}/1.6) suggests lifestyle factors (e.g., diet, low exercise) may lead to progression to {}. "
            "Immediate lifestyle improvements are recommended to reduce risk."
        ).format(bmi, bmi_obesity_level, total_risk_score, prediction)
    else:
        risk_summary = (
            "Your BMI ({:.1f}) indicates {}. Your risk score ({:.2f}/1.6) shows {} high-risk and {} medium-risk lifestyle factors. "
            "Monitor your health and consider lifestyle improvements to maintain or achieve optimal health."
        ).format(bmi, bmi_obesity_level, total_risk_score, high_risk_count, medium_risk_count)

    result_style = {
        'Normal_Weight': 'normal',
        'Insufficient_Weight': 'underweight',
        'Overweight_Level_I': 'overweight',
        'Overweight_Level_II': 'overweight',
        'Obesity_Type_I': 'obesity',
        'Obesity_Type_II': 'obesity',
        'Obesity_Type_III': 'obesity'
    }.get(prediction, 'normal')
    prediction_html = f"""
        <div class='result-box {result_style}'>
            <div class='result-text'>AI-Predicted Obesity Level: {prediction}<span class='emoji-pulse'>🎯</span></div>
            <p>BMI: {bmi:.1f} (Calculated)</p>
            <div class='progress-bar'>
                <div class='progress-fill' style='width: {bmi_percentage}%'></div>
            </div>
            <p>{risk_summary}</p>
            <p><em>ℹ️ Note: Prediction combines BMI (weight/height²) with lifestyle risk score (max 1.6). Transportation (e.g., car) is considered a medium risk only when exercise is low.</em></p>
            <p><span style='display: inline-flex; align-items: center;'>Learn more at the <div class='prediction-link'>🔮 Obesity Level Prediction page</div></span>.</p>
        </div>
    """
    st.session_state["prediction_html"] = prediction_html
    st.session_state["user_inputs"] = user_inputs
    st.session_state["obesity_level"] = prediction

    base_date = datetime.combine(base_date, datetime.min.time())
    with st.spinner("Generating your personalized meal plan... 🥗"):
        df = ai_generate_7day_plan(prediction, user_inputs, preferences, cuisine, difficulty, exclude_ingredients, base_date)
        st.session_state["full_df"] = df
        st.session_state["filtered_df"] = df
        st.session_state["preferences"] = preferences
        st.session_state["cuisine"] = cuisine
        st.session_state["difficulty"] = difficulty
        st.session_state["exclude_ingredients"] = exclude_ingredients
        st.balloons()

# Display AI-Predicted Obesity Level if available
if "prediction_html" in st.session_state:
    st.markdown("### 📊 AI-Predicted Obesity Level")
    st.markdown(st.session_state["prediction_html"], unsafe_allow_html=True)

# Meal Plan Display Logic
if "full_df" in st.session_state:
    df = st.session_state["filtered_df"]
    
    st.markdown('<div class="title">📅 Your 7-Day Meal Plan</div>', unsafe_allow_html=True)
    with st.expander("📋 Weekly Meal Plan Overview", expanded=False):
        st.dataframe(df)

    days = df["day"].cat.categories
    for day in days:
        day_df = df[df["day"] == day]
        st.markdown(f"### {day}")
        cols = st.columns(3)
        for idx, row in day_df.iterrows():
            with cols[idx % 3]:
                image_url = row.get("image_url", FALLBACK_IMAGES.get(row["dish"], FALLBACK_IMAGES[f"Fallback {row['meal']} Dish"]))
                st.markdown(
                    f"""
                    <div class='meal-card' id='{row['dish'].replace(' ', '_')}'>
                        <img src='{image_url}' alt='{row['dish']}' style='width:100%; height:120px; object-fit:cover; border-radius:0.375rem;'>
                        <div class='meal-content'>
                            <div class='meal-title'>🍽️ {row['dish']}</div>
                            <div class='meal-calories'>{row['calories']} kcal</div>
                            <div class='meal-details'>
                                <strong>Protein:</strong> {row['protein']}g<br>
                                <strong>Carbohydrates:</strong> {row['carbohydrates']}g<br>
                                <strong>Fat:</strong> {row['fat']}g<br>
                                <strong>Ingredients:</strong> {row['ingredients']}<br>
                                <strong>Steps:</strong> {row['steps']}
                            </div>
                        </div>
                        <div class='button-container'>
                    """,
                    unsafe_allow_html=True
                )
                favorite_text = "Remove from Favorites" if row["dish"] in st.session_state.get("favorites", []) else "Add to Favorites"
                if st.button(favorite_text, key=f"favorite_{row['day']}_{row['meal']}_{row['dish']}"):
                    if "favorites" not in st.session_state:
                        st.session_state["favorites"] = []
                    if row["dish"] in st.session_state["favorites"]:
                        st.session_state["favorites"].remove(row["dish"])
                    else:
                        st.session_state["favorites"].append(row["dish"])
                    st.rerun()
                if st.button("Change Dish", key=f"change_{row['day']}_{row['meal']}_{row['dish']}_{st.session_state.get('change_counter', 0)}"):
                    st.session_state["change_counter"] = st.session_state.get("change_counter", 0) + 1
                    with st.spinner(f"Generating new dish for {row['meal']} on {row['day']}..."):
                        new_dish = ai_generate_single_dish(
                            st.session_state.get("obesity_level", "Normal_Weight"),
                            st.session_state.get("user_inputs", {}),
                            st.session_state.get("preferences", []),
                            st.session_state.get("cuisine", "Any"),
                            st.session_state.get("difficulty", "Any"),
                            st.session_state.get("exclude_ingredients", []),
                            row["day"],
                            row["meal"]
                        )
                        index = df[(df["day"] == row["day"]) & (df["meal"] == row["meal"])].index
                        if not index.empty:
                            for key, value in new_dish.items():
                                df.loc[index[0], key] = value
                            st.session_state["full_df"] = df
                            st.session_state["filtered_df"] = df
                            cache_key = f"{st.session_state.get('obesity_level', 'Normal_Weight')}_{row['meal']}_{st.session_state.get('cuisine', 'Any')}_{st.session_state.get('difficulty', 'Any')}_{'_'.join(sorted(st.session_state.get('preferences', [])))}_{'_'.join(sorted(st.session_state.get('exclude_ingredients', [])))}_{row['day']}"
                            if cache_key in st.session_state["dish_cache"]:
                                del st.session_state["dish_cache"][cache_key]
                            st.rerun()
                st.markdown("</div></div>", unsafe_allow_html=True)

    # Shopping List
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
        '" download="shopping_list.csv">Download Shopping List</a></div>', 
        unsafe_allow_html=True
    )

    # Daily Nutrition Summary
    st.markdown('<div class="title">📊 Daily Nutrition Summary</div>', unsafe_allow_html=True)
    with st.expander("🤔 Metric Explanations", expanded=False):
        st.write("""
        - **Calories (kcal)**: Total daily calorie intake.
        - **Calorie Difference (kcal)**: Difference between actual and target intake (positive = excess, negative = deficit).
        - **Carbohydrates (g)**: Total daily carbohydrate intake.
        - **Carbohydrate Difference (g)**: Difference between actual and target intake.
        - **Protein (g)**: Total daily protein intake.
        - **Protein Difference (g)**: Difference between actual and target intake.
        - **Fat (g)**: Total daily fat intake.
        - **Fat Difference (g)**: Difference between actual and target intake.
        """)
    daily = df.groupby("day", observed=False)[["calories", "carbohydrates", "protein", "fat"]].sum().round(1).reset_index()
    daily["day"] = pd.Categorical(daily["day"], categories=df["day"].cat.categories, ordered=True)
    daily = daily.sort_values("day")
    target_calories = 2000
    target_protein = 50
    target_carbohydrates = 200
    target_fat = 70
    daily["calorie_diff"] = daily["calories"] - target_calories
    daily["protein_diff"] = daily["protein"] - target_protein
    daily["carbohydrate_diff"] = daily["carbohydrates"] - target_carbohydrates
    daily["fat_diff"] = daily["fat"] - target_fat
    st.dataframe(daily)

    # Nutrition Data Visualization
    st.markdown('<div class="title">📈 Nutrition Trend Chart</div>', unsafe_allow_html=True)
    normalize_data = st.checkbox("Normalize Display (Relative to Target)", value=False, help="Normalize nutrient values to percentages of target values for comparison")
    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Area Chart"], help="Choose your preferred visualization type")
    
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

    for col in ["calories", "protein", "carbohydrates", "fat"]:
        daily_normalized[col] = pd.to_numeric(daily_normalized[col], errors="coerce").fillna(0)

    fig = go.Figure()
    trace_type = go.Bar if chart_type == "Bar Chart" else go.Scatter
    fill_mode = 'tozeroy' if chart_type == "Area Chart" else None
    
    if normalize_data:
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