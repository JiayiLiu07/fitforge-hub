import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import plotly.graph_objects as go
from openai import OpenAI
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Set page configuration
st.set_page_config(page_title="Obesity Level Prediction", page_icon="🔮", layout="wide")

# Custom CSS for Tailwind-inspired styling
st.markdown("""
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        border: none;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .stButton>button:hover { background-color: #2563eb; }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select, .stSlider>div>div {
        border: 1px solid #d1d5db;
        border-radius: 0.375rem;
        padding: 0.5rem;
    }
    .stMarkdown h1 { color: #1f2937; font-size: 2rem; font-weight: 700; }
    .stMarkdown h2 { color: #374151; font-size: 1.5rem; font-weight: 600; }
    .result-box {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease-in;
    }
    .suggestion-box {
        background: linear-gradient(to right, #eff6ff, #dbeafe);
        border: 1px solid #bfdbfe;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-top: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: slideIn 0.5s ease-in;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .suggestion-icon {
        font-size: 2rem;
        animation: pulse 1.5s infinite;
    }
    .suggestion-text {
        font-size: 1rem;
        color: #1f2937;
        line-height: 1.5;
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
    .bmi-table {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .bmi-table table {
        width: 100%;
        border-collapse: collapse;
    }
    .bmi-table th, .bmi-table td {
        border: 1px solid #e5e7eb;
        padding: 0.5rem;
        text-align: left;
    }
    .bmi-table th {
        background-color: #f3f4f6;
        font-weight: 600;
        color: #1f2937;
    }
    .input-box {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .risk-table {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .risk-table table {
        width: 100%;
        border-collapse: collapse;
    }
    .risk-table th, .risk-table td {
        border: 1px solid #e5e7eb;
        padding: 0.5rem;
        text-align: left;
    }
    .risk-table th {
        background-color: #f3f4f6;
        font-weight: 600;
        color: #1f2937;
    }
    .tooltip-icon {
        display: inline-block;
        color: #6b7280;
        font-size: 0.9rem;
        margin-left: 0.5rem;
        cursor: pointer;
    }
    .calc-details {
        background-color: #f3f4f6;
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
        color: #374151;
    }
    .high-risk {
        background-color: #fee2e2;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
    .medium-risk {
        background-color: #fef9c3;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    @media (max-width: 640px) {
        .result-text { font-size: 1rem; }
        .suggestion-box { flex-direction: column; align-items: flex-start; }
        .suggestion-icon { font-size: 1.5rem; }
        .suggestion-text { font-size: 0.9rem; }
        .bmi-table th, .bmi-table td, .risk-table th, .risk-table td { font-size: 0.85rem; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
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
</style>
""", unsafe_allow_html=True)

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar conversation history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
# Health suggestions dictionary with associated emojis
suggestions = {
    'Normal_Weight': {
        'text': 'Your weight is normal! Maintain a balanced diet, exercise regularly (150 min/week moderate activity), and monitor your health periodically.',
        'icon': '✅'
    },
    'Insufficient_Weight': {
        'text': 'Underweight! Increase nutrient intake with high-protein foods (e.g., lean meats, nuts), consult a nutritionist, and monitor weight gain.',
        'icon': '📉'
    },
    'Overweight_Level_I': {
        'text': 'Overweight Level I (or pre-overweight)! Reduce high-calorie foods/drinks, increase aerobic exercise (e.g., brisk walking, swimming, 150–300 min/week), and monitor waist circumference (Men: >90 cm, Women: >80 cm indicates risk).',
        'icon': '⚠️'
    },
    'Overweight_Level_II': {
        'text': 'Overweight Level II! Control diet (reduce high-calorie foods, increase vegetables), engage in regular exercise (150–300 min/week), and seek professional fitness guidance.',
        'icon': '⬆️'
    },
    'Obesity_Type_I': {
        'text': 'Obesity Type I! Start a weight loss plan with diet control, strength training, and consult a doctor. Monitor waist circumference and aim for gradual weight loss.',
        'icon': '🚫'
    },
    'Obesity_Type_II': {
        'text': 'Obesity Type II! Take immediate action with professional medical intervention (e.g., nutritional counseling, possible medication). Increase exercise and monitor health closely.',
        'icon': '⛔'
    },
    'Obesity_Type_III': {
        'text': 'Obesity Type III! High-risk condition; consult a doctor urgently for a comprehensive treatment plan. Focus on diet, exercise, and medical guidance.',
        'icon': '🚨'
    }
}

# WHO BMI ranges (gender-neutral, per WHO standards)
bmi_ranges = pd.DataFrame({
    'BMI Range': ['< 18.5', '18.5 - 24.9', '25.0 - 27.4', '27.5 - 29.9', '30.0 - 34.9', '35.0 - 39.9', '>= 40.0'],
    'Obesity Level': ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I', 'Overweight_Level_II',
                      'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']
})

# Function to get valid default values for session state
def get_valid_default(key, valid_options, default):
    value = st.session_state.get(key)
    if value in valid_options:
        return value
    if value is not None:
        logging.warning(f"Invalid session state value for '{key}': {value}. Falling back to '{default}'.")
    return default

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

# Risk details dictionary
risk_details = {
    'Family history of overweight': {
        'explanation': 'Having a family history of overweight increases your risk of obesity by up to 80%, as it can involve genetic factors linked to higher BMI, cardiovascular diseases, and type 2 diabetes (source: Obesity Action Coalition and related studies).',
        'suggestion': 'Even with a genetic predisposition, you can lower your risk through a balanced diet, regular exercise, and routine health check-ups. Consider consulting a doctor for personalized screening.'
    },
    'Frequent high-calorie food': {
        'explanation': 'Frequent consumption of high-calorie foods (e.g., processed or fast foods high in sugar, salt, and fats) can lead to obesity, insulin resistance, type 2 diabetes, and heart disease, as they contribute excess calories without satiety (source: MD Anderson Cancer Center and Medical News Today).',
        'suggestion': 'Limit high-calorie foods to occasional treats (less than 2-3 times per week). Focus on whole foods like fruits, vegetables, and lean proteins for better nutrient balance.'
    },
    'Vegetable consumption frequency': {
        'explanation': 'Low vegetable intake (≤3 times/week) is a high risk because it deprives your body of essential nutrients and fiber, increasing chances of obesity, heart disease, and weakened immunity (source: WHO recommends at least 400g or 5 portions of fruits/vegetables daily).',
        'suggestion': 'Aim for vegetables in every meal, targeting at least 5-7 times per week (e.g., 2-3 cups daily). Start by adding salads or steamed veggies to your routine for gradual improvement.'
    },
    'Main meal frequency': {
        'explanation': 'Irregular main meals (<2 or >4 per day) can disrupt metabolism, leading to overeating, weight gain, and higher risk of metabolic syndrome (source: Studies suggest 2-3 meals per day is optimal for energy balance).',
        'suggestion': 'Stick to 3 balanced main meals per day to maintain steady energy levels. Avoid skipping meals or excessive eating; plan ahead with portion control.'
    },
    'Food consumption between meals': {
        'explanation': 'Always snacking between meals adds extra calories, potentially causing weight gain and poor dietary habits, especially if snacks are unhealthy (source: Harvard Nutrition Source notes snacking can stem from boredom or distraction, contributing up to 25% of daily energy).',
        'suggestion': 'Limit snacking to 1-2 times per day, choosing healthy options like nuts or yogurt. Eat mindfully to address hunger vs. emotional triggers.'
    },
    'Smoking': {
        'explanation': 'Smoking increases risks of metabolic syndrome, diabetes, and cardiovascular diseases, and when combined with obesity, it amplifies health issues (source: NCBI and AHA studies).',
        'suggestion': 'Quitting smoking can significantly reduce these risks. Seek support from cessation programs or a healthcare provider for effective strategies.'
    },
    'Physical activity frequency': {
        'explanation': 'Insufficient physical activity (≤2 times/week) raises obesity, heart disease, and diabetes risks by reducing energy expenditure (source: WHO recommends at least 150 minutes of moderate activity per week, or 3-5 sessions).',
        'suggestion': 'Build up to at least 3-5 exercise sessions per week, such as walking or cycling for 30 minutes each. Start small and track progress for motivation.'
    },
    'High-calorie drink consumption': {
        'explanation': 'Frequent high-calorie drinks (e.g., sugary sodas) contribute to weight gain, obesity, type 2 diabetes, heart disease, and tooth decay, as they add empty calories (source: CDC and Harvard Nutrition Source).',
        'suggestion': 'Switch to water, herbal tea, or zero-calorie options. Limit sugary drinks to less than once per week to cut unnecessary calories.'
    },
    'Transportation mode': {
        'explanation': 'Sedentary modes like automobile or motorbike reduce daily physical activity, increasing obesity and pollution-related health risks (source: CDC promotes active transport like walking or biking for better fitness).',
        'suggestion': 'Opt for walking, biking, or public transport when possible to incorporate more movement. Aim for at least 10-15 minutes of active commuting daily.'
    }
}

# Function to analyze lifestyle risk factors
def analyze_risk_factors(input_data):
    risk_factors = [
        {'name': 'Family history of overweight', 'value': input_data['family_history_with_overweight'][0], 'condition': 'yes', 'risk': 'High', 'weight': 0.3, 'odds_ratio': 2.5},
        {'name': 'Frequent high-calorie food', 'value': input_data['FAVC'][0], 'condition': 'yes', 'risk': 'High', 'weight': 0.25, 'odds_ratio': 1.8},
        {'name': 'Vegetable consumption frequency', 'value': input_data['FCVC'][0], 'condition': lambda x: x <= 3, 'risk': 'High (Low intake)', 'weight': 0.2, 'odds_ratio': 1.3},
        {'name': 'Main meal frequency', 'value': input_data['NCP'][0], 'condition': lambda x: x < 2 or x > 4, 'risk': 'Medium', 'weight': 0.1, 'odds_ratio': 1.2},
        {'name': 'Food consumption between meals', 'value': input_data['CAEC'][0], 'condition': 'Always', 'risk': 'High', 'weight': 0.2, 'odds_ratio': 1.4},
        {'name': 'Smoking', 'value': input_data['SMOKE'][0], 'condition': 'yes', 'risk': 'Medium', 'weight': 0.1, 'odds_ratio': 1.2},
        {'name': 'Physical activity frequency', 'value': input_data['FAF'][0], 'condition': lambda x: x <= 2, 'risk': 'High (Insufficient)', 'weight': 0.25, 'odds_ratio': 1.5},
        {'name': 'High-calorie drink consumption', 'value': input_data['SCC'][0], 'condition': 'yes', 'risk': 'High', 'weight': 0.2, 'odds_ratio': 1.5},
        {'name': 'Transportation mode', 'value': input_data['MTRANS'][0], 'condition': lambda x: x in ['Automobile', 'Motorbike'], 'risk': 'Medium', 'weight': 0.1, 'odds_ratio': 1.1}
    ]

    risk_summary = []
    high_risk_count = 0
    medium_risk_count = 0
    total_risk_score = 0.0
    high_risk_factors = []
    medium_risk_factors = []

    # Calculate standardized scores based on odds ratios
    all_odds_ratios = [factor['odds_ratio'] for factor in risk_factors]
    max_or_value = 2.5 
    max_odds_ratio_minus_1 = max(or_val - 1 for or_val in all_odds_ratios + [max_or_value]) if all_odds_ratios else 1.0

    for factor in risk_factors:
        if callable(factor['condition']):
            is_risk = factor['condition'](factor['value'])
        else:
            is_risk = factor['value'] == factor['condition']

        risk_level = factor['risk'] if is_risk else 'Neutral'
        contribution = 0.0
        
        if is_risk:
            normalized_contribution = (factor['odds_ratio'] - 1) / (max_or_value - 1) if max_or_value > 1 else 0
            if 'High' in factor['risk']:
                high_risk_count += 1
                contribution = factor['weight'] * normalized_contribution
                high_risk_factors.append(factor['name'])
            elif 'Medium' in factor['risk']:
                medium_risk_count += 1
                contribution = factor['weight'] * normalized_contribution * 0.5
                medium_risk_factors.append(factor['name'])

        total_risk_score += contribution

        risk_summary.append({
            'Risk Factor': factor['name'],
            'User Input': str(factor['value']),
            'Risk Level': risk_level,
            'Contribution': round(contribution, 2)
        })

    return pd.DataFrame(risk_summary), high_risk_count, medium_risk_count, total_risk_score, high_risk_factors, medium_risk_factors

# Function to get AI-predicted obesity level
def get_ai_obesity_level(input_data, bmi, high_risk_count, medium_risk_count, total_risk_score):
    API_KEY = st.session_state.get("api_key") or os.getenv("DASHSCOPE_API_KEY")
    
    if not API_KEY:
        API_KEY = "sk-e200005b066942eebc8c5426df92a6d5"
        logging.warning("DASHSCOPE_API_KEY not found in session state or environment variables. Using hardcoded fallback key.")
        
    if not API_KEY:
        return None, "API Key not found. Please set the DASHSCOPE_API_KEY environment variable or provide it in the session state."
    
    try:
        client = OpenAI(api_key=API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        return None, f"Failed to initialize AI client: {e}"

    PROMPT_TEMPLATE = """
You are a senior health analyst tasked with predicting obesity levels based on user data, BMI, and lifestyle risk factors. The possible obesity levels are: Insufficient_Weight, Normal_Weight, Overweight_Level_I, Overweight_Level_II, Obesity_Type_I, Obesity_Type_II, Obesity_Type_III.

Follow these rules to ensure scientific and consistent predictions, based on WHO standards and obesity research:
- Use BMI as the primary indicator (WHO standards: <18.5 Insufficient, 18.5-24.9 Normal, 25.0-27.4 Overweight_Level_I, 27.5-29.9 Overweight_Level_II, 30.0-34.9 Obesity_Type_I, 35.0-39.9 Obesity_Type_II, >=40.0 Obesity_Type_III).
- Adjust the prediction upward (to a more severe level) based on lifestyle risk factors, weighted as follows (standardized by odds ratios):
  - Family history of overweight: 0.3 (strong genetic influence).
  - Frequent high-calorie food consumption: 0.25 (increases caloric intake).
  - Low physical activity (≤2 times/week): 0.25 (reduces energy expenditure).
  - Low vegetable consumption (≤3 times/week): 0.2 (poor diet quality).
  - Frequent snacking between meals (Always): 0.2 (increases caloric intake).
  - High-calorie drink consumption: 0.2 (adds excess calories).
  - Irregular meal frequency (<2 or >4 meals/day): 0.1 (moderate impact on metabolism).
  - Smoking: 0.1 (moderate metabolic impact).
  - Sedentary transportation (Automobile/Motorbike): 0.1 (reduces daily activity).
- If high_risk_count >= 4 or total_risk_score >= 1.0, predict at least Overweight_Level_I, even if BMI is in Normal range, due to significant lifestyle risks.
- If BMI >= 30.0, predict at least Obesity_Type_I, escalating to Obesity_Type_II or III if total_risk_score >= 1.2 or high_risk_count >= 5.
- For BMI < 18.5, predict Insufficient_Weight unless high_risk_count >= 4, then consider Normal_Weight or higher.
- Ensure predictions are consistent and align with common sense (e.g., high risk factors should not result in Normal_Weight if BMI is near upper normal range).

Provide only the obesity level as the response (e.g., Obesity_Type_I).

User Data:
- Gender: {Gender}
- Age: {Age} years
- Height: {Height} meters
- Weight: {Weight} kg
- Family history of overweight: {family_history_with_overweight}
- Frequent high-calorie food consumption: {FAVC}
- Vegetable consumption frequency: {FCVC} times/week
- Main meal frequency: {NCP} times/day
- Food consumption between meals: {CAEC}
- Smoking: {SMOKE}
- Daily water consumption: {CH2O} liters
- High-calorie drink consumption: {SCC}
- Physical activity frequency: {FAF} times/week
- Electronic device usage: {TUE} hours/day
- Alcohol consumption: {CALC}
- Transportation mode: {MTRANS}
- BMI: {bmi:.2f}
- High-Risk Factors Count: {high_risk_count}
- Medium-Risk Factors Count: {medium_risk_count}
- Total Risk Score: {total_risk_score:.2f} (max possible is ~1.6)
"""

    full_prompt = PROMPT_TEMPLATE.format(**input_data.to_dict(orient='records')[0], bmi=bmi, high_risk_count=high_risk_count, medium_risk_count=medium_risk_count, total_risk_score=total_risk_score)

    logging.info("=========== Input Data ===========")
    logging.info(f"Input: {input_data.to_dict(orient='records')[0]}")
    logging.info(f"BMI: {bmi:.2f}, High-Risk: {high_risk_count}, Medium-Risk: {medium_risk_count}, Total Risk Score: {total_risk_score:.2f}")
    logging.info("=========== Prompt ===========")
    logging.info(f"Sending prompt to LLM:\n{full_prompt}")

    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "You are a health expert predicting obesity levels based on user data, BMI, and lifestyle risk factors. Respond with only the obesity level string."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0,
            max_tokens=50
        )
        prediction = response.choices[0].message.content.strip()
        logging.info(f"AI Prediction: {prediction}")

        valid_predictions = [row['Obesity Level'] for _, row in bmi_ranges.iterrows()]
        if prediction in valid_predictions:
            input_summary = f"Gender: {input_data['Gender'][0]}, Age: {input_data['Age'][0]}, Height: {input_data['Height'][0]}, Weight: {input_data['Weight'][0]}, FamilyHist: {input_data['family_history_with_overweight'][0]}, FAVC: {input_data['FAVC'][0]}, FCVC: {input_data['FCVC'][0]}, NCP: {input_data['NCP'][0]}, CAEC: {input_data['CAEC'][0]}, SMOKE: {input_data['SMOKE'][0]}, CH2O: {input_data['CH2O'][0]}, SCC: {input_data['SCC'][0]}, FAF: {input_data['FAF'][0]}, TUE: {input_data['TUE'][0]}, CALC: {input_data['CALC'][0]}, MTRANS: {input_data['MTRANS'][0]}"
            st.session_state.history.append((input_summary, prediction))
            return prediction, "Prediction successful."
        else:
            logging.warning(f"Invalid prediction received from LLM: {prediction}")
            return None, f"Invalid prediction received: {prediction}"
    except Exception as e:
        logging.error(f"Error during AI prediction: {e}")
        return None, f"Error during AI prediction: {e}"

# Main function to run the app
def main():
    with st.sidebar:
        st.header("🕒 Query History")
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            st.write("")

        if st.session_state.chat_history:
            for idx, (q, a) in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"{len(st.session_state.chat_history)-idx}. {q[:55]}…"):
                    st.markdown("**Q：** " + q)
                    st.markdown("**A：** " + a)
        else:
            st.info("No queries yet. Start asking!🥳")


    # Always display title and subtitle
    st.markdown(
        """
        <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
            🔮 Obesity Level Prediction 🌟
        </h1>
        <p style='text-align:center; font-size:1.1rem; color:#6c757d;'>
        Please enter the following information to predict your obesity level. All fields are required. 💡
        </p>
        """,
        unsafe_allow_html=True
    )

    # Check for API Key
    if not st.session_state.get("api_key"):
        st.warning("⚠️ Please go to the sidebar and enter a valid API key in FitForge_Hub🚀 page")
        st.stop()

    # Set default values for session state
    default_gender = get_valid_default("gender", ["Male", "Female"], "Male")
    default_age = st.session_state.get("age", 30)
    height_cm = st.session_state.get("height", 170.0)
    height_cm_stored = st.session_state.get("height")
    if not isinstance(height_cm_stored, (int, float)):
        height_cm = 170.0
        logging.error(f"Invalid type for st.session_state['height']: {type(height_cm_stored)}. Expected number, got {type(height_cm_stored)}. Resetting to default.")
    default_height = height_cm / 100

    default_weight = st.session_state.get("weight", 70.0)
    default_family_history = get_valid_default("family_history_with_overweight", ["yes", "no"], "no")
    default_favc = get_valid_default("favc", ["yes", "no"], "no")
    default_fcvc = st.session_state.get("fcvc", 3)
    default_ncp = st.session_state.get("ncp", 3)
    caec_options = ["Always", "Frequently", "Sometimes"]
    default_caec = get_valid_default("caec", caec_options, "Sometimes")
    default_smoke = get_valid_default("smoke", ["yes", "no"], "no")
    default_ch2o = st.session_state.get("ch2o", 2.0)
    default_scc = get_valid_default("scc", ["yes", "no"], "no")
    default_faf = st.session_state.get("faf", 2)
    default_tue = st.session_state.get("tue", 2)
    calc_options = ["No", "Sometimes", "Frequently"]
    default_calc = get_valid_default("calc", calc_options, "No")
    mtrans_options = ["Automobile", "Bike", "Motorbike", "Public_Transportation", "Walking"]
    mtrans_mapping = {
        "Public": "Public_Transportation", "Car": "Automobile", "bike": "Bike",
        "motorbike": "Motorbike", "walking": "Walking", "public_transportation": "Public_Transportation"
    }
    raw_mtrans_value = st.session_state.get("mtrans")
    if raw_mtrans_value in mtrans_options:
        default_mtrans = raw_mtrans_value
    elif raw_mtrans_value is not None and isinstance(raw_mtrans_value, str):
        default_mtrans = mtrans_mapping.get(raw_mtrans_value, "Public_Transportation")
        logging.warning(f"MTRANS value '{raw_mtrans_value}' not directly in options. Mapped to '{default_mtrans}'.")
    else:
        default_mtrans = "Public_Transportation"
        if raw_mtrans_value is not None:
            logging.warning(f"Invalid session state value for 'mtrans': {raw_mtrans_value}. Falling back to '{default_mtrans}'.")

    with st.form(key='prediction_form'):
        col1, col2 = st.columns(2)

        with col1:
            gender = st.selectbox("♂️ Gender", ["Male", "Female"], index=["Male", "Female"].index(default_gender), help="Select your gender")
            age = st.slider("📅 Age (years)", min_value=0, max_value=120, value=default_age, help="Slide to select your age")
            height = st.slider("📏 Height (meters)", min_value=0.0, max_value=3.0, value=default_height, step=0.01, help="Slide to select your height")
            weight = st.slider("⚖️ Weight (kg)", min_value=0.0, max_value=300.0, value=default_weight, step=0.1, help="Slide to select your weight")
            family_history = st.selectbox("👨‍👩‍👧‍👦 Family history of overweight", ["yes", "no"], index=["yes", "no"].index(default_family_history), help="Do you have a family history of overweight?")
            favc = st.selectbox("🍔 Frequent consumption of high-calorie food", ["yes", "no"], index=["yes", "no"].index(default_favc), help="Do you frequently eat high-calorie food?")
            fcvc = st.slider("🥦 Vegetable consumption frequency (per week)", min_value=0, max_value=7, value=default_fcvc, help="Slide to select weekly vegetable consumption")
            ncp = st.slider("🍽️ Main meal frequency (per day)", min_value=0, max_value=10, value=default_ncp, help="Slide to select daily main meal frequency")

        with col2:
            caec = st.selectbox("🍫 Food consumption between meals", caec_options, index=caec_options.index(default_caec), help="Frequency of snacking between meals")
            smoke = st.selectbox("🚬 Smoking", ["yes", "no"], index=["yes", "no"].index(default_smoke), help="Do you smoke?")
            ch2o = st.slider("💧 Daily water consumption (liters)", min_value=0.0, max_value=10.0, value=default_ch2o, step=0.1, help="Slide to select daily water intake")
            scc = st.selectbox("🥤 High-calorie drink consumption", ["yes", "no"], index=["yes", "no"].index(default_scc), help="Do you frequently consume high-calorie drinks?")
            faf = st.slider("🏃 Physical activity frequency (per week)", min_value=0, max_value=7, value=default_faf, help="Slide to select weekly exercise frequency")
            tue = st.slider("📱 Electronic device usage time (hours/day)", min_value=0, max_value=24, value=default_tue, help="Slide to select daily electronic device usage")
            calc = st.selectbox("🍺 Alcohol consumption", calc_options, index=calc_options.index(default_calc), help="Frequency of alcohol consumption")
            mtrans = st.selectbox("🚗 Daily transportation mode", mtrans_options, index=mtrans_options.index(default_mtrans), help="Primary mode of transportation")

        submit_button = st.form_submit_button("🔮 Predict Obesity Level")

    if submit_button:
        st.session_state["gender"] = gender
        st.session_state["age"] = age
        if height is not None and isinstance(height, (int, float)):
            st.session_state["height"] = height * 100
        else:
            logging.warning("Slider provided an invalid height value. Session state not updated.")
        st.session_state["weight"] = weight
        st.session_state["family_history_with_overweight"] = family_history
        st.session_state["favc"] = favc
        st.session_state["fcvc"] = fcvc
        st.session_state["ncp"] = ncp
        st.session_state["caec"] = caec
        st.session_state["smoke"] = smoke
        st.session_state["ch2o"] = ch2o
        st.session_state["scc"] = scc
        st.session_state["faf"] = faf
        st.session_state["tue"] = tue
        st.session_state["calc"] = calc
        st.session_state["mtrans"] = mtrans

        input_data = pd.DataFrame({
            'Gender': [gender],
            'Age': [age],
            'Height': [height],
            'Weight': [weight],
            'family_history_with_overweight': [family_history],
            'FAVC': [favc],
            'FCVC': [fcvc],
            'NCP': [ncp],
            'CAEC': [caec],
            'SMOKE': [smoke],
            'CH2O': [ch2o],
            'SCC': [scc],
            'FAF': [faf],
            'TUE': [tue],
            'CALC': [calc],
            'MTRANS': [mtrans]
        })

        st.markdown("#### 📄 Your Input Data")
        st.markdown("""
            <div class='input-box'>
                <p><strong>Gender:</strong> {}</p>
                <p><strong>Age:</strong> {} years</p>
                <p><strong>Height:</strong> {} meters</p>
                <p><strong>Weight:</strong> {} kg</p>
                <p><strong>Family history of overweight:</strong> {}</p>
                <p><strong>Frequent high-calorie food:</strong> {}</p>
                <p><strong>Vegetable consumption frequency:</strong> {} times/week</p>
                <p><strong>Main meal frequency:</strong> {} times/day</p>
                <p><strong>Food consumption between meals:</strong> {}</p>
                <p><strong>Smoking:</strong> {}</p>
                <p><strong>Daily water consumption:</strong> {} liters</p>
                <p><strong>High-calorie drink consumption:</strong> {}</p>
                <p><strong>Physical activity frequency:</strong> {} times/week</p>
                <p><strong>Electronic device usage:</strong> {} hours/day</p>
                <p><strong>Alcohol consumption:</strong> {}</p>
                <p><strong>Transportation mode:</strong> {}</p>
            </div>
        """.format(gender, age, height, weight, family_history, favc, fcvc, ncp, caec, smoke, ch2o, scc, faf, tue, calc, mtrans),
        unsafe_allow_html=True)

        csv_buffer = StringIO()
        input_data.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Download Input Data as CSV",
            data=csv_buffer.getvalue(),
            file_name="user_input_data.csv",
            mime="text/csv",
            key="download_button"
        )

        def normalize_radar(df):
            vec = {}
            diet_score_fcvc = (df['FCVC'][0] / 7) if df['FCVC'][0] >= 0 else 0
            diet_score_favc = (1 - (df['FAVC'][0] == 'yes')) if df['FAVC'][0] in ['yes', 'no'] else 0.5
            vec['Diet'] = (diet_score_fcvc * 0.7 + diet_score_favc * 0.3)
            vec['Exercise'] = df['FAF'][0] / 7 if df['FAF'][0] >= 0 else 0
            vec['Hydration'] = min(df['CH2O'][0] / 3, 1) if df['CH2O'][0] >= 0 else 0
            vec['Sleep Habits'] = 1 - min(df['TUE'][0] / 12, 1) if df['TUE'][0] >= 0 else 1
            vec['Genetics'] = 1 - (df['family_history_with_overweight'][0] == 'yes') if df['family_history_with_overweight'][0] in ['yes', 'no'] else 0.5
            mtrans_score = {'Walking': 1, 'Bike': 0.9, 'Public_Transportation': 0.7, 'Motorbike': 0.4, 'Automobile': 0.2}
            vec['Commute'] = mtrans_score.get(df['MTRANS'][0], 0.3)
            alcohol_score = {'No': 1, 'Sometimes': 0.6, 'Frequently': 0.2}
            vec['Alcohol'] = alcohol_score.get(df['CALC'][0], 0.4)
            for key, value in vec.items():
                if isinstance(value, (int, float)):
                    vec[key] = max(0, min(1, value))
            keys = list(vec.keys())
            vals = list(vec.values())
            avg = [0.65, 0.55, 0.70, 0.60, 0.50, 0.45, 0.75]
            return keys, vals, avg

        if height > 0:
            bmi = weight / (height ** 2)
            bmi_percentage = min(bmi / 40 * 100, 100)
        else:
            bmi = 0
            bmi_percentage = 0
            logging.warning("Height is zero, cannot calculate BMI.")

        bmi_obesity_level = get_bmi_obesity_level(bmi)
        risk_df, high_risk_count, medium_risk_count, total_risk_score, high_risk_factors, medium_risk_factors = analyze_risk_factors(input_data)

        logging.info(f"Calculated Total Risk Score: {total_risk_score:.2f}")
        logging.info(f"Risk Factor Contributions: {risk_df[['Risk Factor', 'Contribution']].to_dict('records')}")

        ai_prediction, ai_message = get_ai_obesity_level(input_data, bmi, high_risk_count, medium_risk_count, total_risk_score)

        if ai_prediction is None:
            st.warning(f"AI prediction failed: {ai_message}. Falling back to BMI-based prediction.")
            final_prediction = bmi_obesity_level
            risk_summary = f"Your BMI is {bmi:.1f}, which falls in the {bmi_obesity_level.replace('_', ' ').lower()} range according to WHO standards. The AI prediction failed (reason: {ai_message}), so we are using the BMI-based result for now."
        else:
            final_prediction = ai_prediction
            risk_summary = f"Your BMI is {bmi:.1f}, which falls in the {bmi_obesity_level.replace('_', ' ').lower()} range according to WHO standards."
            if high_risk_count > 0 or medium_risk_count > 0:
                risk_summary += f" However, due to lifestyle risks ({high_risk_count} high-risk and {medium_risk_count} medium-risk factors, total risk score of {total_risk_score:.2f} out of ~1.6), the AI predicts you may have {final_prediction.replace('_', ' ').lower()}. This suggests a higher overall health risk. Here's a breakdown to help you understand and improve:\n\n"
                if high_risk_count > 0:
                    risk_summary += "**High-Risk Factors:**\n"
                    for factor in high_risk_factors:
                        details = risk_details.get(factor, {'explanation': 'No details available.', 'suggestion': 'Consult a professional.'})
                        risk_summary += f"- **{factor.lower()}**: {details['explanation']} To reduce this risk, {details['suggestion']}\n"
                if medium_risk_count > 0:
                    risk_summary += "\n**Medium-Risk Factors:**\n"
                    for factor in medium_risk_factors:
                        details = risk_details.get(factor, {'explanation': 'No details available.', 'suggestion': 'Consult a professional.'})
                        risk_summary += f"- **{factor.lower()}**: {details['explanation']} To reduce this risk, {details['suggestion']}\n"
                risk_summary += "\nMaking small changes based on these suggestions can significantly improve your health over time!"
            else:
                risk_summary += f" With {high_risk_count} high-risk and {medium_risk_count} medium-risk lifestyle factors (total risk score {total_risk_score:.2f}/~1.6), the AI predicts you may have {final_prediction.replace('_', ' ').lower()}."

        st.markdown("### 🕸️ Lifestyle Radar")
        labels, user_vals, avg_vals = normalize_radar(input_data)

        with st.expander("❓ How to read the radar?"):
            st.markdown("""
            - Each axis represents one healthy habit. The further out (closer to 1), the better.
            - Solid blue line represents **your data**; dashed blue line shows the **average** for your age and gender (general benchmark).
            - Gaps toward the center indicate areas for improvement.
            """)

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=user_vals,
            theta=labels,
            fill='toself',
            name='Your Data',
            line=dict(color='#3b82f6', width=3),
            fillcolor='rgba(59,130,246,0.25)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=avg_vals,
            theta=labels,
            fill='toself',
            name='Average',
            line=dict(color='#9ca3af', width=2, dash='dot'),
            fillcolor='rgba(156,163,175,0.15)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                    ticktext=['Poor', '', 'Fair', '', 'Excellent']
                ),
                angularaxis=dict(
                    tickfont=dict(size=13, family='Arial, sans-serif')
                )
            ),
            height=420,
            margin=dict(l=60, r=60, t=40, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("### 📊 Lifestyle Risk Factor Analysis")
        st.markdown("""
            <div class='risk-table'>
                <table>
                    <tr>
                        <th>Risk Factor</th>
                        <th>User Input</th>
                        <th>Risk Level</th>
                        <th>Contribution to Risk Score</th>
                    </tr>
                    {}
                </table>
            </div>
            <p><span class='tooltip-icon' title='Click for more details'>ℹ️ Details</span></p>
        """.format(''.join(
            f"<tr><td>{row['Risk Factor']}</td><td>{row['User Input']}</td><td>{row['Risk Level']}</td><td>{row['Contribution']:.2f}</td></tr>"
            for _, row in risk_df.iterrows()
        )), unsafe_allow_html=True)

        with st.expander("❓ View WHO BMI Reference Table"):
            st.markdown("""
                <div class='bmi-table'>
                    <table>
                        <tr>
                            <th>BMI Range</th>
                            <th>Obesity Level</th>
                        </tr>
                        {}
                    </table>
                </div>
                <p><span class='tooltip-icon' title='Source: World Health Organization (WHO). (2000). Obesity: Preventing and Managing the Global Epidemic. WHO Technical Report Series 894. Additional details available at: https://www.who.int/publications/i/item/9241208945'>ℹ️ Source: WHO Technical Report Series 894 (2000)</span></p>
            """.format(''.join(
                f"<tr><td>{row['BMI Range']}</td><td>{row['Obesity Level'].replace('_', ' ')}</td></tr>"
                for _, row in bmi_ranges.iterrows()
            )), unsafe_allow_html=True)

        with st.expander("❓ How Total Risk Score is Calculated"):
            st.markdown("""
                <div class='bmi-table'>
                    <table>
                        <tr>
                            <th>Risk Factor</th>
                            <th>Risk Level</th>
                            <th>Weight</th>
                            <th>Condition for Risk</th>
                            <th>Approx. Contribution (if risk present)</th>
                        </tr>
                        <tr><td>Family history of overweight</td><td>High</td><td>0.30</td><td>Yes</td><td>0.30 * (2.5-1)/(2.5-1) = 0.30</td></tr>
                        <tr><td>Frequent high-calorie food</td><td>High</td><td>0.25</td><td>Yes</td><td>0.25 * (1.8-1)/(2.5-1) ≈ 0.13</td></tr>
                        <tr><td>Vegetable consumption frequency</td><td>High (Low intake)</td><td>0.20</td><td>≤3 times/week</td><td>0.20 * (1.3-1)/(2.5-1) ≈ 0.06</td></tr>
                        <tr><td>Main meal frequency</td><td>Medium</td><td>0.10</td><td><2 or >4 times/day</td><td>0.10 * (1.2-1)/(2.5-1) * 0.5 ≈ 0.05</td></tr>
                        <tr><td>Food consumption between meals</td><td>High</td><td>0.20</td><td>Always</td><td>0.20 * (1.4-1)/(2.5-1) ≈ 0.12</td></tr>
                        <tr><td>Smoking</td><td>Medium</td><td>0.10</td><td>Yes</td><td>0.10 * (1.2-1)/(2.5-1) * 0.5 ≈ 0.05</td></tr>
                        <tr><td>Physical activity frequency</td><td>High (Insufficient)</td><td>0.25</td><td>≤2 times/week</td><td>0.25 * (1.5-1)/(2.5-1) ≈ 0.13</td></tr>
                        <tr><td>High-calorie drink consumption</td><td>High</td><td>0.20</td><td>Yes</td><td>0.20 * (1.5-1)/(2.5-1) ≈ 0.10</td></tr>
                        <tr><td>Transportation mode</td><td>Medium</td><td>0.10</td><td>Automobile or Motorbike</td><td>0.10 * (1.1-1)/(2.5-1) * 0.5 ≈ 0.05</td></tr>
                    </table>
                </div>
                <p>The <strong>Total Risk Score</strong> is calculated by summing the contributions of risk factors, standardized by their relative risk impact (using normalized Odds Ratios). High-risk factors contribute their full normalized weight, while medium-risk factors contribute half their normalized weight.</p>
                <p><strong>Example:</strong> A user with family history (0.30), frequent high-calorie food (0.13), low physical activity (0.13), and smoking (0.05) might have a total risk score of 0.30 + 0.13 + 0.13 + 0.05 = 0.61.</p>
                <p><span class='tooltip-icon' title='Source: Based on common epidemiological studies and risk factor analysis. Specific weights and ORs are illustrative approximations.'>ℹ️ Source: Illustrative, based on epidemiological data.</span></p>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class='calc-details'>
                <p><strong>Calculated BMI:</strong> {bmi:.2f}</p>
                <p><strong>BMI-Based Obesity Level:</strong> {bmi_obesity_level.replace('_', ' ')}</p>
                <p class='high-risk'><strong>High-Risk Factors:</strong> {high_risk_count}</p>
                <p class='medium-risk'><strong>Medium-Risk Factors:</strong> {medium_risk_count}</p>
                <p><strong>Total Risk Score:</strong> {total_risk_score:.2f} (out of ~1.6)</p>
            </div>
        """, unsafe_allow_html=True)

        result_style = {
            'Normal_Weight': 'normal',
            'Insufficient_Weight': 'underweight',
            'Overweight_Level_I': 'overweight',
            'Overweight_Level_II': 'overweight',
            'Obesity_Type_I': 'obesity',
            'Obesity_Type_II': 'obesity',
            'Obesity_Type_III': 'obesity'
        }.get(final_prediction, 'normal')

        st.markdown("### 🏆 Prediction Result")
        # Append to sidebar history
        q_summary = f"Predicting obesity level（BMI={bmi:.1f}）"
        a_summary = f"AI prediction results：{final_prediction.replace('_', ' ')}"
        st.session_state.chat_history.append((q_summary, a_summary))

        st.markdown(f"""
            <div class='result-box {result_style}'>
                <div class='result-text'>AI-Predicted Obesity Level: {final_prediction.replace('_', ' ')}<span class='emoji-pulse'>🍎</span></div>
                <p>BMI: {bmi:.1f} (Calculated)</p>
                <div class='progress-bar'>
                    <div class='progress-fill' style='width: {bmi_percentage}%'></div>
                </div>
                <p>{risk_summary}</p>
                <p><em>Note: The AI prediction considers lifestyle factors and is powered by a large language model. BMI is calculated using the standard formula (weight/height²).</em></p>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("💡 View Health Suggestions", expanded=True):
            if final_prediction in suggestions:
                st.markdown(f"""
                    <div class='suggestion-box {result_style}'>
                        <span class='suggestion-icon'>{suggestions[final_prediction]['icon']}</span>
                        <span class='suggestion-text'>{suggestions[final_prediction]['text']}</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No specific suggestions available for this prediction level. Consult a healthcare professional.")

if __name__ == "__main__":
    main()
