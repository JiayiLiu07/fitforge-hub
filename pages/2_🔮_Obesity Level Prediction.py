import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Obesity Level Prediction", page_icon="🔮", layout="wide")

# Custom CSS for Tailwind-inspired styling and annotations
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
        {'name': 'Family history of overweight', 'value': input_data['family_history_with_overweight'][0], 'condition': 'yes', 'risk': 'High', 'weight': 0.3},
        {'name': 'Frequent high-calorie food', 'value': input_data['FAVC'][0], 'condition': 'yes', 'risk': 'High', 'weight': 0.25},
        {'name': 'Vegetable consumption frequency', 'value': input_data['FCVC'][0], 'condition': lambda x: x <= 3, 'risk': 'High (Low intake)', 'weight': 0.2},
        {'name': 'Main meal frequency', 'value': input_data['NCP'][0], 'condition': lambda x: x < 2 or x > 4, 'risk': 'Medium', 'weight': 0.1},
        {'name': 'Food consumption between meals', 'value': input_data['CAEC'][0], 'condition': 'Always', 'risk': 'High', 'weight': 0.2},
        {'name': 'Smoking', 'value': input_data['SMOKE'][0], 'condition': 'yes', 'risk': 'Medium', 'weight': 0.1},
        {'name': 'Physical activity frequency', 'value': input_data['FAF'][0], 'condition': lambda x: x <= 2, 'risk': 'High (Insufficient)', 'weight': 0.25},
        {'name': 'High-calorie drink consumption', 'value': input_data['SCC'][0], 'condition': 'yes', 'risk': 'High', 'weight': 0.2},
        {'name': 'Transportation mode', 'value': input_data['MTRANS'][0], 'condition': lambda x: x in ['Automobile', 'Motorbike'], 'risk': 'Medium', 'weight': 0.1}
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
        if is_risk:
            if 'High' in factor['risk']:
                high_risk_count += 1
                total_risk_score += factor['weight']
            elif 'Medium' in factor['risk']:
                medium_risk_count += 1
                total_risk_score += factor['weight'] * 0.5  # Medium risk contributes half the weight
        
        risk_summary.append({
            'Risk Factor': factor['name'],
            'User Input': str(factor['value']),
            'Risk Level': risk_level
        })
    
    return pd.DataFrame(risk_summary), high_risk_count, medium_risk_count, total_risk_score

# Main program
def main():
    st.title("🔮 Obesity Level Prediction 🌟")
    st.markdown("Please enter the following information to predict your obesity level. All fields are required. 💡")

    # Clear session state on form submission to ensure fresh inputs
    if 'form_submitted' in st.session_state:
        del st.session_state['form_submitted']

    # User input form
    with st.form(key='prediction_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox("🚻 Gender", ["Male", "Female"], help="Select your gender")
            age = st.slider("👴 Age (years)", min_value=0, max_value=120, value=25, key="age",help="Select your age")
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
        if submit_button:
            st.session_state['form_submitted'] = True

    if submit_button or 'form_submitted' in st.session_state:
        # Prepare input data
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
        
        # Display user inputs
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
        
        # Export input data as CSV
        csv_buffer = StringIO()
        input_data.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Input Data as CSV",
            data=csv_buffer.getvalue(),
            file_name="user_input_data.csv",
            mime="text/csv",
            key="download_button"
        )
        # ---------- 归一化到 0-1 ----------
        def normalize_radar(df):
            """
            把原始字段映射到 7 个维度
            饮食质量  运动  水/饮料  作息  家族风险  交通方式  烟酒
            值越大越健康（已反转负向指标）
            """
            vec = {}
            vec['Diet']        = (df['FCVC'][0] / 7) * (1 - (df['FAVC'][0] == 'yes'))  # 蔬菜多 & 少垃圾食品
            vec['Exercise']    = df['FAF'][0] / 7
            vec['Hydration']   = min(df['CH2O'][0] / 3, 1)                              # 2-3 L 为 1
            vec['Sleep_Habits']= 1 - min(df['TUE'][0] / 12, 1)                          # 电子设备少
            vec['Genetics']    = 1 - (df['family_history_with_overweight'][0] == 'yes') # 家族史
            vec['Commute']     = {'Walking':1, 'Bike':0.9, 'Public_Transportation':0.7,
                                'Motorbike':0.4, 'Automobile':0.2}[df['MTRANS'][0]]
            vec['Alcohol']     = {'No':1, 'Sometimes':0.6, 'Frequently':0.2}[df['CALC'][0]]

            keys = list(vec.keys())
            vals = list(vec.values())
            # 同年龄/同性别均值（mock 数据，可后期用真实统计替换）
            avg  = [0.65, 0.55, 0.70, 0.60, 0.50, 0.45, 0.75]
            return keys, vals, avg
        
        # ---------- 🕸️ 个人健康雷达图 ----------
        st.markdown("### 🕸️  Obesity Radar")
        labels, user_vals, avg_vals = normalize_radar(input_data)

        # 双语提示
        with st.expander("❓ How to read the radar?"):
            st.markdown("""
            - Each axis = one healthy habit. The further out (closer to 1), the better.  
            - Solid blue = **You**; shaded blue = **average** of same age & gender.  
            - Gaps toward the center show where you can improve.
            """)

        fig = go.Figure()

        # 用户本人
        fig.add_trace(go.Scatterpolar(
            r=user_vals,
            theta=labels,
            fill='toself',
            name='You ',
            line=dict(color='#3b82f6', width=3),
            fillcolor='rgba(59,130,246,0.25)'
        ))

        # 平均值
        fig.add_trace(go.Scatterpolar(
            r=avg_vals,
            theta=labels,
            fill='toself',
            name='Average',
            line=dict(color='#9ca3af', width=2, dash='dot'),
            fillcolor='rgba(156,163,175,0.15)'
        ))

        # 美化配置
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

        # 在 Streamlit 中展示
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Calculate BMI
        bmi = weight / (height ** 2)
        bmi_percentage = min(bmi / 40 * 100, 100)  # Normalize BMI to 0-100% (cap at 40 for display)

        # Get BMI-based obesity level
        bmi_obesity_level = get_bmi_obesity_level(bmi)
        
        # Analyze lifestyle risk factors
        risk_df, high_risk_count, medium_risk_count, total_risk_score = analyze_risk_factors(input_data)
        
        # Display risk factor analysis
        st.markdown("### ⚠️ Lifestyle Risk Factor Analysis")
        st.markdown("""
            <div class='risk-table'>
                <table>
                    <tr>
                        <th>Risk Factor</th>
                        <th>User Input</th>
                        <th>Risk Level</th>
                    </tr>
                    {}
                </table>
            </div>
        """.format(''.join(
            f"<tr><td>{row['Risk Factor']}</td><td>{row['User Input']}</td><td>{row['Risk Level']}</td></tr>"
            for _, row in risk_df.iterrows()
        )), unsafe_allow_html=True)
        
        # Calculation Details
        st.markdown("#### 📈 Calculation Details")
        
        # Display WHO BMI reference table in an expander with enhanced source annotation
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
                f"<tr><td>{row['BMI Range']}</td><td>{row['Obesity Level']}</td></tr>"
                for _, row in bmi_ranges.iterrows()
            )), unsafe_allow_html=True)
        
        # Display calculation results
        st.markdown(f"""
            <div class='calc-details'>
                <p><strong>Calculated BMI:</strong> {bmi:.2f}</p>
                <p><strong>BMI-Based Obesity Level:</strong> {bmi_obesity_level}</p>
                <p><strong>High-Risk Factors:</strong> {high_risk_count}</p>
                <p><strong>Medium-Risk Factors:</strong> {medium_risk_count}</p>
                <p><strong>Total Risk Score:</strong> {total_risk_score:.2f} (out of 1.6)</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Adjust obesity level based on risk factors
        prediction = bmi_obesity_level
        risk_summary = ""
        obesity_levels = ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I', 'Overweight_Level_II', 
                          'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']
        current_level_index = obesity_levels.index(bmi_obesity_level) if bmi_obesity_level in obesity_levels else 1
        
        # More rigorous prediction logic based on BMI and risk score
        if bmi_obesity_level == 'Normal_Weight' and total_risk_score >= 0.8 and bmi >= 22.0:
            prediction = 'Overweight_Level_I'
            risk_summary = (
                "Your BMI ({:.1f}) is within the Normal Weight range, but your risk score ({:.2f}/1.6) indicates significant lifestyle risk factors (e.g., diet, low physical activity, family history). "
                "This suggests a potential progression to Overweight Level I within 6–12 months if lifestyle factors are not addressed."
            ).format(bmi, total_risk_score)
        elif total_risk_score >= 0.8 and current_level_index < len(obesity_levels) - 1:
            prediction = obesity_levels[current_level_index + 1]
            risk_summary = (
                "Your BMI ({:.1f}) indicates {}, but your high risk score ({:.2f}/1.6) from lifestyle factors (e.g., diet, low physical activity) suggests a risk of progressing to {}. "
                "Consider immediate lifestyle changes to mitigate this risk."
            ).format(bmi, bmi_obesity_level, total_risk_score, prediction)
        else:
            risk_summary = (
                "Your BMI ({:.1f}) indicates {}. Your risk score ({:.2f}/1.6) suggests {} high-risk and {} medium-risk lifestyle factors. "
                "Monitor your health and consider improving lifestyle factors to maintain or achieve optimal health."
            ).format(bmi, bmi_obesity_level, total_risk_score, high_risk_count, medium_risk_count)
        
        # Determine result box style based on prediction
        result_style = {
            'Normal_Weight': 'normal',
            'Insufficient_Weight': 'underweight',
            'Overweight_Level_I': 'overweight',
            'Overweight_Level_II': 'overweight',
            'Obesity_Type_I': 'obesity',
            'Obesity_Type_II': 'obesity',
            'Obesity_Type_III': 'obesity'
        }.get(prediction, 'normal')

        # Display prediction result
        st.markdown("### 📊 Prediction Result")
        st.markdown(f"""
            <div class='result-box {result_style}'>
                <div class='result-text'>Your Obesity Level: {prediction}<span class='emoji-pulse'>🎯</span></div>
                <p>BMI: {bmi:.1f} (Estimated)</p>
                <div class='progress-bar'>
                    <div class='progress-fill' style='width: {bmi_percentage}%'></div>
                </div>
                <p>{risk_summary}</p>
                <p><em>Note: The prediction combines BMI with a weighted lifestyle risk score. Transportation mode (e.g., automobile) is considered a medium-risk factor only when combined with low physical activity.</em></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Collapsible health suggestion with enhanced styling
        with st.expander("💡 View Health Suggestions", expanded=True):
            if prediction in suggestions:
                st.markdown(f"""
                    <div class='suggestion-box {result_style}'>
                        <span class='suggestion-icon'>{suggestions[prediction]['icon']}</span>
                        <span class='suggestion-text'>{suggestions[prediction]['text']}</span>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()