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

st.set_page_config(
    page_title="Obesity Level Prediction",
    page_icon="🔮",
    layout="wide"
)

if "api_key" not in st.session_state or not st.session_state["api_key"]:
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
    # 黄色警告框
    st.warning("⚠️ Please go to the sidebar and enter a valid API key in 🗣️ NL2SQL page.")
    st.stop()

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

# Health suggestions dictionary with associated emojis
suggestions = {
    'Normal_Weight': {
        'text': 'Your weight is normal! Maintain a balanced diet, exercise regularly (150 min/week moderate activity), and monitor your health periodically.',
        'icon': '👍'
    },
    'Insufficient_Weight': {
        'text': 'Underweight! Increase nutrient intake with high-protein foods (e.g., lean meats, nuts), consult a nutritionist, and monitor weight gain.',
        'icon': '⚠️'
    },
    'Overweight_Level_I': {
        'text': 'Overweight Level I (or pre-overweight)! Reduce high-calorie foods/drinks, increase aerobic exercise (e.g., brisk walking, swimming, 150–300 min/week), and monitor waist circumference (Men: ≥90 cm, Women: ≥80 cm indicates risk).',
        'icon': '🔔'
    },
    'Overweight_Level_II': {
        'text': 'Overweight Level II! Control diet (reduce high-calorie foods, increase vegetables), engage in regular exercise (150–300 min/week), and seek professional fitness guidance.',
        'icon': '🚨'
    },
    'Obesity_Type_I': {
        'text': 'Obesity Type I! Start a weight loss plan with diet control, strength training, and consult a doctor. Monitor waist circumference and aim for gradual weight loss.',
        'icon': '🛑'
    },
    'Obesity_Type_II': {
        'text': 'Obesity Type II! Take immediate action with professional medical intervention (e.g., nutritional counseling, possible medication). Increase exercise and monitor health closely.',
        'icon': '‼️'
    },
    'Obesity_Type_III': {
        'text': 'Obesity Type III! High-risk condition; consult a doctor urgently for a comprehensive treatment plan. Focus on diet, exercise, and medical guidance.',
        'icon': '🔴'
    }
}

# WHO BMI ranges (gender-neutral, per WHO standards)
bmi_ranges = pd.DataFrame({
    'BMI Range': ['< 18.5', '18.5 - 24.9', '25.0 - 27.4', '27.5 - 29.9', '30.0 - 34.9', '35.0 - 39.9', '>= 40.0'],
    'Obesity Level': ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I', 'Overweight_Level_II', 
                      'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']
})

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
    
    # Calculate standardized scores based on odds ratios
    max_odds_ratio = max(factor['odds_ratio'] - 1 for factor in risk_factors)  # For normalization
    for factor in risk_factors:
        if callable(factor['condition']):
            is_risk = factor['condition'](factor['value'])
        else:
            is_risk = factor['value'] == factor['condition']
        
        risk_level = factor['risk'] if is_risk else 'Neutral'
        contribution = 0.0
        if is_risk:
            standardized_score = (factor['odds_ratio'] - 1) / max_odds_ratio  # Normalize OR contribution
            if 'High' in factor['risk']:
                high_risk_count += 1
                contribution = factor['weight'] * standardized_score
                total_risk_score += contribution
                high_risk_factors.append(factor['name'])
            elif 'Medium' in factor['risk']:
                medium_risk_count += 1
                contribution = factor['weight'] * standardized_score * 0.5
                total_risk_score += contribution
        
        risk_summary.append({
            'Risk Factor': factor['name'],
            'User Input': str(factor['value']),
            'Risk Level': risk_level,
            'Contribution': round(contribution, 2)
        })
    
    return pd.DataFrame(risk_summary), high_risk_count, medium_risk_count, total_risk_score, high_risk_factors

# Function to get AI-predicted obesity level
def get_ai_obesity_level(input_data, bmi, high_risk_count, medium_risk_count, total_risk_score):
    client = OpenAI(api_key=st.session_state["api_key"],
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    
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
- High-Risk Factors: {high_risk_count}
- Medium-Risk Factors: {medium_risk_count}
- Total Risk Score: {total_risk_score:.2f} (out of ~1.6)
"""
    
    full_prompt = PROMPT_TEMPLATE.format(**input_data.to_dict(orient='records')[0], bmi=bmi, high_risk_count=high_risk_count, medium_risk_count=medium_risk_count, total_risk_score=total_risk_score)
    
    # Log input data and prompt for debugging
    logging.info("=========== Input Data ===========")
    logging.info(f"Input: {input_data.to_dict(orient='records')[0]}")
    logging.info(f"BMI: {bmi:.2f}, High-Risk: {high_risk_count}, Medium-Risk: {medium_risk_count}, Total Risk Score: {total_risk_score:.2f}")
    logging.info("=========== Prompt ===========")
    logging.info(f"Sending prompt to LLM:\n{full_prompt}")
    
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "You are a health expert predicting obesity levels based on user data, BMI, and lifestyle risk factors."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0,  # Ensure deterministic output
            max_tokens=50
        )
        prediction = response.choices[0].message.content.strip()
        logging.info(f"AI Prediction: {prediction}")
        if prediction in [row['Obesity Level'] for _, row in bmi_ranges.iterrows()]:
            # Update history
            input_summary = f"Gender: {input_data['Gender'][0]}, Age: {input_data['Age'][0]}, Height: {input_data['Height'][0]}, Weight: {input_data['Weight'][0]}, Other factors: {input_data['family_history_with_overweight'][0]}, {input_data['FAVC'][0]}, {input_data['FCVC'][0]}, {input_data['NCP'][0]}, {input_data['CAEC'][0]}, {input_data['SMOKE'][0]}, {input_data['CH2O'][0]}, {input_data['SCC'][0]}, {input_data['FAF'][0]}, {input_data['TUE'][0]}, {input_data['CALC'][0]}, {input_data['MTRANS'][0]}"
            st.session_state.history.append((input_summary, prediction))
            return prediction, "Prediction successful."
        else:
            logging.warning(f"Invalid prediction received: {prediction}")
            return None, f"Invalid prediction received: {prediction}"
    except Exception as e:
        logging.error(f"Error in API call: {str(e)}")
        return None, f"Error in API call: {str(e)}"

# Main program
def main():
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
    # Sidebar for history
    with st.sidebar:
        st.header("🕒 Prediction History")
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.success("History cleared! ✅")
        
        if st.session_state.history:
            for i, (data, prediction) in enumerate(st.session_state.history):
                with st.expander(f"Prediction {i+1}"):
                    st.markdown(f"**Input Data:** {data}")
                    st.markdown(f"**AI Prediction:** {prediction.replace('_', ' ')}")
        else:
            st.info("No predictions yet. Start predicting! 🥳")

    with st.form(key='prediction_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox("🚻 Gender", ["Male", "Female"], help="Select your gender")
            age = st.slider("👴 Age (years)", min_value=0, max_value=120, value=25, help="Slide to select your age")
            height = st.slider("📏 Height (meters)", min_value=0.0, max_value=3.0, value=1.70, step=0.01, help="Slide to select your height")
            weight = st.slider("⚖️ Weight (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1, help="Slide to select your weight")
            family_history = st.selectbox("👪 Family history of overweight", ["yes", "no"], help="Do you have a family history of overweight?")
            favc = st.selectbox("🍔 Frequent consumption of high-calorie food", ["yes", "no"], help="Do you frequently eat high-calorie food?")
            fcvc = st.slider("🥦 Vegetable consumption frequency (per week)", min_value=0, max_value=7, value=3, help="Slide to select weekly vegetable consumption")
            ncp = st.slider("🍽️ Main meal frequency (per day)", min_value=0, max_value=10, value=3, help="Slide to select daily main meal frequency")
        
        with col2:
            caec = st.selectbox("🍿 Food consumption between meals", ["Always", "Frequently", "Sometimes"], help="Frequency of snacking between meals")
            smoke = st.selectbox("🚬 Smoking", ["yes", "no"], help="Do you smoke?")
            ch2o = st.slider("💧 Daily water consumption (liters)", min_value=0.0, max_value=10.0, value=2.0, step=0.1, help="Slide to select daily water intake")
            scc = st.selectbox("🥤 High-calorie drink consumption", ["yes", "no"], help="Do you frequently consume high-calorie drinks?")
            faf = st.slider("🏃 Physical activity frequency (per week)", min_value=0, max_value=7, value=2, help="Slide to select weekly exercise frequency")
            tue = st.slider("📱 Electronic device usage time (hours/day)", min_value=0, max_value=24, value=2, help="Slide to select daily electronic device usage")
            calc = st.selectbox("🍷 Alcohol consumption", ["No", "Sometimes", "Frequently"], help="Frequency of alcohol consumption")
            mtrans = st.selectbox("🚗 Daily transportation mode", ["Automobile", "Bike", "Motorbike", 
                                                               "Public_Transportation", "Walking"], help="Primary mode of transportation")
        
        submit_button = st.form_submit_button("🔍 Predict Obesity Level")
    
    # Process form submission
    if submit_button:
        # Clear previous form submission state to ensure fresh calculation
        if 'form_submitted' in st.session_state:
            del st.session_state['form_submitted']
        
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
        
        st.markdown("#### 📋 Your Input Data")
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
            label="📥 Download Input Data as CSV",
            data=csv_buffer.getvalue(),
            file_name="user_input_data.csv",
            mime="text/csv",
            key="download_button"
        )
        
        def normalize_radar(df):
            vec = {}
            vec['Diet'] = (df['FCVC'][0] / 7) * (1 - (df['FAVC'][0] == 'yes'))
            vec['Exercise'] = df['FAF'][0] / 7
            vec['Hydration'] = min(df['CH2O'][0] / 3, 1)
            vec['Sleep Habits'] = 1 - min(df['TUE'][0] / 12, 1)
            vec['Genetics'] = 1 - (df['family_history_with_overweight'][0] == 'yes')
            vec['Commute'] = {'Walking': 1, 'Bike': 0.9, 'Public_Transportation': 0.7,
                              'Motorbike': 0.4, 'Automobile': 0.2}[df['MTRANS'][0]]
            vec['Alcohol'] = {'No': 1, 'Sometimes': 0.6, 'Frequently': 0.2}[df['CALC'][0]]
            keys = list(vec.keys())
            vals = list(vec.values())
            avg = [0.65, 0.55, 0.70, 0.60, 0.50, 0.45, 0.75]
            return keys, vals, avg
        
        st.markdown("### 🕸️ Obesity Radar")
        labels, user_vals, avg_vals = normalize_radar(input_data)
        
        with st.expander("❓ How to read the radar?"):
            st.markdown("""
            - Each axis represents one healthy habit. The further out (closer to 1), the better.
            - Solid blue line represents **your data**; dashed blue line shows the **average** for your age and gender.
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
        
        # Calculate BMI
        bmi = weight / (height ** 2)
        bmi_percentage = min(bmi / 40 * 100, 100)
        bmi_obesity_level = get_bmi_obesity_level(bmi)
        
        # Analyze risk factors for display
        risk_df, high_risk_count, medium_risk_count, total_risk_score, high_risk_factors = analyze_risk_factors(input_data)
        
        # Log the calculated total risk score and contributions for debugging
        logging.info(f"Calculated Total Risk Score: {total_risk_score:.2f}")
        logging.info(f"Risk Factor Contributions: {risk_df[['Risk Factor', 'Contribution']].to_dict('records')}")
        
        # Get AI-predicted obesity level
        ai_prediction, ai_message = get_ai_obesity_level(input_data, bmi, high_risk_count, medium_risk_count, total_risk_score)
        if ai_prediction is None:
            st.warning(f"AI prediction failed: {ai_message}. Falling back to BMI-based prediction.")
            ai_prediction = bmi_obesity_level
            risk_summary = f"Your BMI is {bmi:.1f}, which falls in the {bmi_obesity_level.replace('_', ' ').lower()} range according to WHO standards. The AI prediction failed (reason: {ai_message}), so we're using the BMI-based result for now."
        else:
            # Generate detailed risk summary with specific high-risk factors
            if high_risk_count > 0:
                risk_factors_text = ", ".join([factor.lower() for factor in high_risk_factors[:3]])  # Limit to top 3 for brevity
                if len(high_risk_factors) > 3:
                    risk_factors_text += f", and {len(high_risk_factors) - 3} other high-risk factors"
                risk_summary = f"Your BMI is {bmi:.1f}, which falls in the {bmi_obesity_level.replace('_', ' ').lower()} range according to WHO standards. However, due to significant lifestyle risks, including {risk_factors_text} ({high_risk_count} high-risk factors, total risk score of {total_risk_score:.2f} out of ~1.6), the AI predicts you may have {ai_prediction.replace('_', ' ').lower()}. This suggests a higher health risk due to these lifestyle factors."
            else:
                risk_summary = f"Your BMI is {bmi:.1f}, which falls in the {bmi_obesity_level.replace('_', ' ').lower()} range according to WHO standards. With {high_risk_count} high-risk and {medium_risk_count} medium-risk lifestyle factors (total risk score {total_risk_score:.2f}/~1.6), the AI predicts you may have {ai_prediction.replace('_', ' ').lower()}."
        
        st.markdown("### ⚠️ Lifestyle Risk Factor Analysis")
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
        """.format(''.join(
            f"<tr><td>{row['Risk Factor']}</td><td>{row['User Input']}</td><td>{row['Risk Level']}</td><td>{row['Contribution']:.2f}</td></tr>"
            for _, row in risk_df.iterrows()
        )), unsafe_allow_html=True)
        
        st.markdown("#### 📈 Calculation Details")
        with st.expander("📒 View WHO BMI Reference Table"):
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
        
        with st.expander("📊 How Total Risk Score is Calculated"):
            st.markdown("""
                <div class='bmi-table'>
                    <table>
                        <tr>
                            <th>Risk Factor</th>
                            <th>Risk Level</th>
                            <th>Weight</th>
                            <th>Condition for Risk</th>
                            <th>Contribution Formula</th>
                        </tr>
                        <tr><td>Family history of overweight</td><td>High</td><td>0.3</td><td>Yes</td><td>0.3 if Yes, else 0</td></tr>
                        <tr><td>Frequent high-calorie food</td><td>High</td><td>0.25</td><td>Yes</td><td>0.25 × 0.533 if Yes, else 0</td></tr>
                        <tr><td>Vegetable consumption frequency</td><td>High (Low intake)</td><td>0.2</td><td>≤3 times/week</td><td>0.2 × 0.2 if ≤3, else 0</td></tr>
                        <tr><td>Main meal frequency</td><td>Medium</td><td>0.1</td><td><2 or >4 times/day</td><td>0.1 × 0.133 × 0.5 if condition met, else 0</td></tr>
                        <tr><td>Food consumption between meals</td><td>High</td><td>0.2</td><td>Always</td><td>0.2 × 0.267 if Always, else 0</td></tr>
                        <tr><td>Smoking</td><td>Medium</td><td>0.1</td><td>Yes</td><td>0.1 × 0.133 × 0.5 if Yes, else 0</td></tr>
                        <tr><td>Physical activity frequency</td><td>High (Insufficient)</td><td>0.25</td><td>≤2 times/week</td><td>0.25 × 0.333 if ≤2, else 0</td></tr>
                        <tr><td>High-calorie drink consumption</td><td>High</td><td>0.2</td><td>Yes</td><td>0.2 × 0.333 if Yes, else 0</td></tr>
                        <tr><td>Transportation mode</td><td>Medium</td><td>0.1</td><td>Automobile or Motorbike</td><td>0.1 × 0.067 × 0.5 if condition met, else 0</td></tr>
                    </table>
                </div>
                <p>The <strong>Total Risk Score</strong> is calculated by summing the contributions of risk factors, standardized by their relative risk impact:</p>
                <ul>
                    <li><strong>High-risk factors</strong>: Contribute weight × (odds ratio - 1) / max(odds ratio - 1). E.g., family history contributes 0.3 × 1.0 = 0.30 if "Yes".</li>
                    <li><strong>Medium-risk factors</strong>: Contribute half their weight × (odds ratio - 1) / max(odds ratio - 1). E.g., smoking contributes 0.1 × 0.133 × 0.5 ≈ 0.01 if "Yes".</li>
                    <li><strong>Total possible score</strong>: Approximately 1.6 (sum of high-risk weights).</li>
                </ul>
                <p><strong>Example</strong>: For a user with family history (0.30), high-calorie food (0.25 × 0.533 ≈ 0.13), low physical activity (0.25 × 0.333 ≈ 0.08), and smoking (0.1 × 0.133 × 0.5 ≈ 0.01), the Total Risk Score is 0.30 + 0.13 + 0.08 + 0.01 ≈ 0.52.</p>
                <p><span class='tooltip-icon' title='Source: Frayling et al. (2007). A Common Variant in the FTO Gene Is Associated with Body Mass Index. Science, 316(5826), 889-894; WHO (2000). Obesity: Preventing and Managing the Global Epidemic. WHO Technical Report Series 894.'>ℹ️ Source: Frayling et al. (2007), WHO (2000)</span></p>
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
        }.get(ai_prediction, 'normal')

        st.markdown("### 📊 Prediction Result")
        st.markdown(f"""
            <div class='result-box {result_style}'>
                <div class='result-text'>AI-Predicted Obesity Level: {ai_prediction.replace('_', ' ')}<span class='emoji-pulse'>🎯</span></div>
                <p>BMI: {bmi:.1f} (Calculated)</p>
                <div class='progress-bar'>
                    <div class='progress-fill' style='width: {bmi_percentage}%'></div>
                </div>
                <p>{risk_summary}</p>
                <p><em>Note: The AI prediction considers lifestyle factors and is powered by a large language model. BMI is calculated using the standard formula (weight/height²).</em></p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("💡 View Health Suggestions", expanded=True):
            if ai_prediction in suggestions:
                st.markdown(f"""
                    <div class='suggestion-box {result_style}'>
                        <span class='suggestion-icon'>{suggestions[ai_prediction]['icon']}</span>
                        <span class='suggestion-text'>{suggestions[ai_prediction]['text']}</span>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()