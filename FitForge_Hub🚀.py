import streamlit as st
import textwrap

# ---------- Page Configuration ----------
# The page_title here appears in the browser tab
st.set_page_config(
    page_title="FitForge Hub",
    page_icon="🚀",
    layout="centered",
)

# ---------- CSS ----------
st.markdown("""
<style>
.card {border-radius:12px;padding:1.2rem 1.5rem;margin:.8rem 0;background:#f7f9fc;border:1px solid #e0e7ff;}
.metric {font-size:1.2rem;font-weight:600;color:#0072ff;}
.tip-card {border-radius:10px;padding:1rem;margin:0.5rem 0;background:#e6f0ff;border:1px solid #0072ff;}
.tip-text {font-size:1rem;color:#333;font-weight:500;}
.rotate-btn {background:none;color:#000000;border:1px solid #e0e7ff;border-radius:8px;padding:0.5rem 1rem;width:150px;height:40px;}
.rotate-btn:hover {background:none;cursor:pointer;}
.mission-title {
    font-size:1.8rem;
    font-weight:700;
    color:#000000;
    text-align:left;
    margin:0 0 1rem 0;
    padding:0;
    border:none;
    outline:none;
}
.mission-metric-label {
    font-size:0.9rem;
    color:#555;
    font-weight:500;
    display:inline;
    margin-right:1rem;
}
.mission-metric-value {
    font-size:1.3rem;
    font-weight:700;
    color:#0072ff;
    display:inline;
}
.mission-text {
    font-size:1rem;
    color:#333;
    text-align:left;
    margin-bottom:1rem;
}
.action-note {
    font-size:0.9rem;
    color:#666;
    margin-top:0.3rem;
    text-align:left;
}
.no-wrap-btn {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
/* Custom style for the main title, now in blue */
.main-title-blue {
    font-size: 2.5rem; /* Adjust size as needed */
    font-weight: 700;
    color: #0072ff; /* Blue color */
    text-align: center; /* Center align the main title */
    margin-bottom: 1rem;
}
/* Custom style for the detailed description, now in grey */
.detailed-description-grey {
    text-align: center;
    font-size: 1.1rem;
    color: #6c757d; /* Grey color */
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ---------- Main Title and Detailed Description ----------
# Use markdown for both the main title (with blue color) and the description (with grey color)
st.markdown(
    '<h1 class="main-title-blue">FitForge Hub: Your All-in-One AI-Powered Wellness Companion 🚀</h1>',
    unsafe_allow_html=True
)
st.markdown(
    """
    <p class="detailed-description-grey">
    Seamlessly translate natural language queries into actionable SQL insights 🗣️➡️📊 for data-driven understanding of your health. Predict and manage your obesity risk with personalized habit analysis 🔮📈, and receive dynamic, intelligent 7-day meal plans 🥗🍎 and 30-day body progression forecasts 📅✨. Forge your optimal physique and well-being with intuitive tools and real-time feedback – no expertise required, just results! 💪💯
    </p>
    """,
    unsafe_allow_html=True
)


# ---------- Tips List (Updated Phrasing) ----------
TIPS = [
    "💧 Hydrate first thing to energize your day.",
    "🥗 Prioritize protein to fuel muscle growth.",
    "😴 Optimize sleep for peak recovery.",
    "🚶‍♂️ Boost daily movement for enhanced calorie burn.",
    "🧘‍♀️ Practice mindful breathing to reduce stress.",
    "⚖️ Monitor weight trends for progress insights.",
    "🥑 Choose high-fiber foods for lasting fullness.",
    "⏰ Time meals early to sync with your metabolism.",
    "📱 Track meals periodically to uncover patterns.",
    "🏋️ Elevate training intensity for optimal gains.",
    "🍳 Cook at home to master calorie control.",
    "🍫 Savor dark chocolate to tame sweet cravings.",
    "🥤 Opt for zero-calorie drinks to curb sugar urges.",
    "🧂 Watch sodium levels in processed foods.",
    "🧑‍⚕️ Seek medical advice before major diet shifts.",
    "🥛 Try a pre-bed protein boost for recovery.",
    "🧗 Stay active daily to amplify energy output.",
    "✅ Build balanced plates with veggies, protein, carbs.",
    "🍺 Limit alcohol to accelerate fat loss.",
    "📈 Track waist changes to monitor body composition."
]

# ---------- Session State Initialization ----------
for k in ["age", "weight", "height", "sex", "goal", "desired_weight", "tip_index"]:
    st.session_state.setdefault(k, None)
if st.session_state.tip_index is None:
    st.session_state.tip_index = 0

# ---------- Sidebar for Tips ----------
with st.sidebar:
    st.markdown("### 💡 Fitness Insights")
    current_tip = TIPS[st.session_state.tip_index]
    st.markdown(f'<div class="tip-card"><p class="tip-text">{current_tip}</p></div>', unsafe_allow_html=True)
    if st.button("🔄 Next Insight", key="rotate_tip", help="Cycle to the next tip"):
        st.session_state.tip_index = (st.session_state.tip_index + 1) % len(TIPS)
        st.rerun()

# ---------- 2. Check-in Form ----------
GOAL_OPTIONS = [
    "Aggressive Fat Loss",
    "Moderate Fat Loss",
    "Maintain",
    "Lean Bulk",
    "Bulk",
]
GOAL_HELP = """
- **Aggressive Fat Loss**: Significant calorie deficit for rapid weight loss  
- **Moderate Fat Loss**: Moderate calorie deficit for steady weight loss  
- **Maintain**: Keep current weight  
- **Lean Bulk**: Slight calorie surplus for minimal fat gain  
- **Bulk**: Larger calorie surplus to maximize muscle gain
"""

with st.form("checkin"):
    col1, col2 = st.columns(2)
    age = col1.number_input("Age", 10, 90, 25)
    sex = col2.selectbox("Sex", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    height = st.number_input("Height (cm)", 120, 230, 170)
    desired_weight = st.slider("Desired Weight (kg)", 30.0, 200.0, weight, help="Select your target weight for the 30-day plan")

    goal = st.selectbox(
        "Core Fitness Goal",
        GOAL_OPTIONS,
        help=textwrap.dedent(GOAL_HELP).strip(),
    )

    if st.form_submit_button("Launch Your Transformation", use_container_width=True):
        for k, v in {"age": age, "weight": weight, "height": height, "sex": sex, "goal": goal, "desired_weight": desired_weight}.items():
            st.session_state[k] = v
        st.rerun()

# ---------- 3. Strategic Overview ----------
if st.session_state.goal and st.session_state.desired_weight:
    st.markdown("---")
    st.subheader("Strategic Overview")
    w, h = st.session_state.weight, st.session_state.height / 100
    bmi = w / (h ** 2)
    delta = w - st.session_state.desired_weight
    proj_bmi = (st.session_state.desired_weight) / (h ** 2)

    st.write(f"**{st.session_state.sex}, {st.session_state.age} yrs | Goal: {st.session_state.goal}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Current BMI", f"{bmi:.1f}")
    col2.metric("Target Mass Change", f"{-delta:.1f} kg")
    col3.metric("Projected BMI", f"{proj_bmi:.1f}")

# ---------- 4. Two Rows, Two Columns Buttons + Single Row Long Text ----------
    st.write("Next Steps:")
    cols = st.columns(2)  # Two rows, two columns

    actions = [
        ("🗣️ NL2SQL",
         "pages/1_🗣️_NL2SQL.py",
         "Query datasets using natural language and instantly see clean SQL, live tables and interactive charts—no coding needed."),
        ("🔮 Obesity Level Prediction",
         "pages/2_🔮_Obesity Level Prediction.py",
         "Enter your daily habits—sleep, activity, diet, stress—and instantly receive a real-time obesity-risk score plus personalized tips to lower it."),
        ("🥗 7-Day Smart Meal Planner",
         "pages/3_🥗_7-Day Smart_Meal_Planner.py",
         "Intelligently generates and dynamically adjusts your personalized nutritious meal plan for the next 7 days."),
        ("📅 30-Day Body Planner",
         "pages/4_📅_30-Day Body Planner.py",
         "Calculates your new BMI in real time and provides a line chart showing your projected 30-day weight change.")
    ]

    for i, (label, page, note) in enumerate(actions):
        col = cols[i % 2] # Distribute buttons across the two columns for each row
        with col:
            if st.button(label, key=label, use_container_width=True):
                st.switch_page(page)
            st.caption(note)