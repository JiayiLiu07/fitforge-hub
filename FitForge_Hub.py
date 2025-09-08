import streamlit as st
import textwrap

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="FitForge Hub",
    page_icon="🚀",
    layout="wide",
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
.main-title-blue {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0072ff;
    text-align: center;
    margin-bottom: 1rem;
}
.detailed-description-grey {
    text-align: center;
    font-size: 1.1rem;
    color: #6c757d;
    line-height: 1.6;
}
.success-message {
    background-color: #d1fae5;
    color: #065f46;
    padding: 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.9rem;
    text-align: center;
    margin-top: 0.5rem;
    opacity: 0;
    animation: fadeIn 0.5s ease-in forwards, fadeOut 0.5s ease-out 4.5s forwards;
}
.warning-message {
    background-color: #fef9c3;
    color: #854d0e;
    padding: 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.9rem;
    text-align: center;
    margin-top: 0.5rem;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeOut {
    from { opacity: 1; transform: translateY(0); }
    to { opacity: 0; transform: translateY(-10px); }
}
.stForm {width: 100%; max-width: 1200px; margin: 0 auto;}
.stColumn {gap: 2rem;}
</style>
""", unsafe_allow_html=True)

# ---------- Tips List ----------
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

# ---------- Sidebar for API Key Input and Tips ----------
with st.sidebar:
    st.header("🔑 API Key")
    api_key = st.text_input("Enter your API Key:", type="password", value=st.session_state.get("api_key", ""))
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API Key saved! ✅")

    st.header("💡 Daily Tip")
    # Initialize tip index in session state
    if "tip_index" not in st.session_state:
        st.session_state.tip_index = 0
    # Display current tip
    st.markdown(f'<div class="tip-card"><span class="tip-text">{TIPS[st.session_state.tip_index]}</span></div>', unsafe_allow_html=True)
    # Button to cycle to next tip
    if st.button("Next Tip", key="next_tip", use_container_width=True):
        st.session_state.tip_index = (st.session_state.tip_index + 1) % len(TIPS)
        st.rerun()

# ---------- Main Title and Description ----------
st.markdown(
    """
    <div class='main-title-blue'>FitForge Hub</div>
    <div class='detailed-description-grey'>
       Your all-in-one platform for personalized health and fitness planning🚀.<br> 
     Seamlessly convert natural language queries into actionable SQL insights 🗣️➡️📊, predict and manage your obesity risk with personalized habit analysis 🔮📈, and get a dynamic, intelligent 7-day meal plan 🥗🍎 and a 30-day fitness progress forecast 📅✨. With intuitive tools and real-time feedback, build your ideal physique and health—no expertise required, just results! 💪💯
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- User Input Form ----------
with st.form("user_input_form"):
    st.subheader("🪪 Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("⚧️ Gender", ["Male", "Female"], index=0 if st.session_state.get("gender") is None else ["Male", "Female"].index(st.session_state.get("gender")))
        age = st.number_input("🎂 Age (years)", min_value=10, max_value=90, value=st.session_state.get("age") or 25)
        default_height = 170.0
        session_height = st.session_state.get("height")
        height_value = session_height if (session_height and 100.0 <= session_height <= 220.0) else default_height
        height = st.number_input("📏 Height (cm)", min_value=100.0, max_value=220.0, value=height_value, step=0.1)
        weight = st.number_input("⚖️ Weight (kg)", min_value=30.0, max_value=200.0, value=st.session_state.get("weight") or 70.0, step=0.1)
        family_history = st.selectbox("🧑‍🧑‍🧒 Family history of overweight", ["yes", "no"], index=0 if st.session_state.get("family_history_with_overweight") is None else ["yes", "no"].index(st.session_state.get("family_history_with_overweight")))
        favc = st.selectbox("🍿 Frequent high-calorie food", ["yes", "no"], index=0 if st.session_state.get("favc") is None else ["yes", "no"].index(st.session_state.get("favc")))
        fcvc = st.slider("🥬 Vegetable consumption frequency (per week)", 0, 7, value=st.session_state.get("fcvc") or 2)
        ncp = st.slider("🍚 Main meal frequency (per day)", 1, 5, value=st.session_state.get("ncp") or 3)
    with col2:
        caec = st.selectbox("🍫 Food consumption between meals", ["Always", "Frequently", "Sometimes", "no"], index=2 if st.session_state.get("caec") is None else ["Always", "Frequently", "Sometimes", "no"].index(st.session_state.get("caec")))
        smoke = st.selectbox("🚬 Smoking", ["yes", "no"], index=1 if st.session_state.get("smoke") is None else ["yes", "no"].index(st.session_state.get("smoke")))
        ch2o = st.slider("💧 Daily water consumption (liters)", 0.5, 5.0, value=st.session_state.get("ch2o") or 2.0, step=0.1)
        scc = st.selectbox("🥤 High-calorie drink consumption", ["yes", "no"], index=1 if st.session_state.get("scc") is None else ["yes", "no"].index(st.session_state.get("scc")))
        faf = st.slider("🏋️ Physical activity frequency (per week)", 0, 7, value=st.session_state.get("faf") or 2)
        tue = st.slider("📱 Electronic device usage time (hours/day)", 0, 12, value=st.session_state.get("tue") or 3)
        calc = st.selectbox("🍷 Alcohol consumption", ["No", "Sometimes", "Frequently"], index=0 if st.session_state.get("calc") is None else ["No", "Sometimes", "Frequently"].index(st.session_state.get("calc")))
        # Updated mtrans options to include Public_Transportation
        mtrans_options = ["Walking", "Bike", "Public_Transportation", "Car", "Motorbike"]
        # Map Public to Public_Transportation for backward compatibility
        session_mtrans = st.session_state.get("mtrans")
        if session_mtrans == "Public":
            session_mtrans = "Public_Transportation"
        mtrans = st.selectbox(
            "🚗 Transportation mode",
            mtrans_options,
            index=2 if st.session_state.get("mtrans") is None else mtrans_options.index(session_mtrans) if session_mtrans in mtrans_options else 2
        )
    
    st.subheader("🏆 Fitness Goal")
    col3, col4 = st.columns(2)
    with col3:
        goal = st.selectbox("🎯 Goal", ["Lose Weight", "Maintain Weight", "Gain Muscle"], index=0 if st.session_state.get("goal") is None else ["Lose Weight", "Maintain Weight", "Gain Muscle"].index(st.session_state.get("goal")))
    with col4:
        desired_weight = st.number_input("🤩 Desired Weight (kg)", min_value=30.0, max_value=200.0, value=st.session_state.get("desired_weight") or 65.0, step=0.1)

    # Submit button
    submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)

    if submitted:
        # Validate height explicitly
        if not (100.0 <= height <= 220.0):
            st.error(f"Height must be between 100.0 and 220.0 cm. Got {height}.")
        else:
            for k, v in {
                "gender": gender, "age": age, "height": height, "weight": weight,
                "family_history_with_overweight": family_history, "favc": favc,
                "fcvc": fcvc, "ncp": ncp, "caec": caec, "smoke": smoke, "ch2o": ch2o,
                "scc": scc, "faf": faf, "tue": tue, "calc": calc, "mtrans": mtrans,
                "goal": goal, "desired_weight": desired_weight
            }.items():
                st.session_state[k] = v
            st.session_state.success_message_trigger = True
            st.rerun()

# Display success message if triggered
if st.session_state.get("success_message_trigger", False):
    st.markdown('<div class="success-message">Personal information saved successfully!</div>', unsafe_allow_html=True)
    st.session_state.success_message_trigger = False

# ---------- Strategic Overview ----------
if all(st.session_state.get(k) is not None for k in ["goal", "desired_weight", "height", "weight"]):
    st.markdown("---")
    st.subheader("Strategic Overview")
    w, h = st.session_state.weight, st.session_state.height / 100
    bmi = w / (h ** 2)
    delta = w - st.session_state.desired_weight
    proj_bmi = st.session_state.desired_weight / (h ** 2)

    st.write(f"**{st.session_state.gender}, {st.session_state.age} yrs | Goal: {st.session_state.goal}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Current BMI", f"{bmi:.1f}")
    col2.metric("Target Mass Change", f"{-delta:.1f} kg")
    col3.metric("Projected BMI", f"{proj_bmi:.1f}")

# ---------- Navigation Buttons ----------
    st.write("Next Steps:")
    cols = st.columns(2)
    actions = [
        ("🗣️ Obesity Data Explorer", "pages/1_🗣️_Obesity_Data_Explorer.py",
         "Query datasets using natural language and instantly see clean SQL, live tables and interactive charts—no coding needed."),
        ("🔮 Obesity Level Prediction", "pages/2_🔮_Obesity Level Prediction.py",
         "Enter your daily habits—sleep, activity, diet, stress—and instantly receive a real-time obesity-risk score plus personalized tips to lower it."),
        ("🥗 7-Day Smart Meal Planner", "pages/3_🥗_7-Day Smart Meal Planner.py",
         "Intelligently generates and dynamically adjusts your personalized nutritious meal plan for the next 7 days."),
        ("📅 30-Day Body Planner", "pages/4_📅_30-Day Body Planner.py",
         "Calculates your new BMI in real time and provides a line chart showing your projected 30-day weight change.")
    ]

    for i, (label, page, note) in enumerate(actions):
        col = cols[i % 2]
        with col:
            if st.button(label, key=label, use_container_width=True):
                st.switch_page(page)
            st.caption(note)




            