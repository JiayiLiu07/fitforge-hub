import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import joblib
import json
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

# ---------- 0. Page Config ----------
st.set_page_config(
    page_title="30-Day Body Planner",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_PATH = "models/obesity_xgb.pkl"
# Define numerical and categorical features used by the model
numerical = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]
categorical = ["Gender", "family_history_with_overweight", "FAVC", "CAEC",
               "SMOKE", "SCC", "CALC", "MTRANS"]
feature_order = numerical + categorical

@st.cache_resource
def load_model_and_encoder():
    """Loads the pre-trained model and label encoder."""
    try:
        loaded = joblib.load(MODEL_PATH)
        return loaded["model"], loaded["le"]
    except FileNotFoundError:
        st.error(f"Error: Model file not found at {MODEL_PATH}. Please ensure the model is saved correctly.")
        logging.error(f"Model file not found: {MODEL_PATH}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading model: {e}")
        logging.error(f"Model loading failed: {e}")
        st.stop()

model, le = load_model_and_encoder()

# ---------- WHO BMI Classification ----------
def bmi_level(bmi):
    """Classifies BMI into WHO standard levels."""
    if bmi < 18.5:
        return "Insufficient_Weight"
    elif bmi < 25:
        return "Normal_Weight"
    elif bmi < 27.5:
        return "Overweight_Level_I"
    elif bmi < 30:
        return "Overweight_Level_II"
    elif bmi < 35:
        return "Obesity_Type_I"
    elif bmi < 40:
        return "Obesity_Type_II"
    else:
        return "Obesity_Type_III"

# ---------- TDEE Calculation (Total Daily Energy Expenditure) ----------
def tdee(w, h_cm, age, gender, activity):
    """Calculates Basal Metabolic Rate (BMR) and then TDEE."""
    # Harris-Benedict equation for BMR
    bmr = (10 * w) + (6.25 * h_cm) - (5 * age) + (5 if gender == "Male" else -161)
    return bmr * activity

# ---------- 30-Day Weight Projection Function ----------
def predict_30d(base_row, delta, seed=42):
    """
    Simulates weight change over 30 days based on baseline and lifestyle adjustments.
    
    Args:
        base_row (pd.DataFrame): DataFrame with baseline user characteristics.
        delta (dict): Dictionary of lifestyle change values.
        seed (int): Seed for random number generation for daily fluctuations.
        
    Returns:
        tuple: A tuple containing:
            - list: Predicted weights for each of the 31 days (including start day).
            - float: Total estimated caloric deficit over 30 days.
    """
    rng = np.random.default_rng(seed)
    w0 = base_row["Weight"].iat[0] # Starting weight
    h_cm = base_row["Height"].iat[0] * 100 # Height in cm
    age = base_row["Age"].iat[0]
    gender = base_row["Gender"].iat[0]
    
    # Safely get FAF and ensure it's a number for activity calculation
    faf_value = base_row["FAF"].iat[0] if isinstance(base_row["FAF"].iat[0], (int, float)) else 0
    activity = 1.2 + faf_value * 0.075 # Activity multiplier based on FAF

    # Calculate daily caloric deficit from lifestyle changes
    daily_deficit = (
        delta.get("extra_water", 0) * 10 +  # Assume 1L extra water adds 10 kcal burn
        delta.get("extra_ex", 0) * 150 +    # Assume 1 exercise session burns 150 kcal
        delta.get("veg_add", 0) * 15 +      # Assume extra veg serving adds 15 kcal to diet quality
        (150 if delta.get("no_drink", False) else 0) + # Assume quitting sugary drinks saves 150 kcal/day
        delta.get("sleep_add", 0) * 50 +    # Assume extra sleep adds 50 kcal burn
        delta.get("alc_red", 0) * 100 +     # Assume reducing alcohol saves 100 kcal/day
        delta.get("screen_red", 0) * 30 +   # Assume reducing screen time saves 30 kcal/day
        (100 if delta.get("quit_smoke", False) else 0) # Assume quitting smoking saves 100 kcal/day
    )

    weights = [w0] # Start with initial weight
    for day in range(1, 31):
        # Introduce weekly variation in deficit (e.g., slightly less on weekends)
        factor = 1.0 if day % 7 < 5 else 0.9 # Weekday vs Weekend factor
        real_deficit = daily_deficit * factor + rng.normal(0, 15) # Add daily biological noise
        
        # Calculate new weight: 1 kg of fat ≈ 7700 kcal
        w_new = weights[-1] - real_deficit / 7700
        w_new = max(w_new, 25) # Prevent weight from going unrealistically low
        weights.append(w_new)

    return weights, daily_deficit * 30

# ---------- Page Header ----------
st.markdown(
    """
    <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
        📅 30-Day Body Planner 
    </h1>
    <p style='text-align:center; font-size:1.1rem; color:#6c757d;'>
        Tweak your lifestyle and visualize your weight trend over the next 30 days.
    </p>
    <hr style='margin:1rem 0 2rem;'>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar with User Inputs ----------
with st.sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            padding-top: 0; # Remove default padding at the top of the sidebar
        }
        .sidebar-card {
            background: #ffffff10; /* Slight background for card effect */
            border-radius: 8px;
            padding: .8rem .6rem .6rem .8rem;
            margin-bottom: .6rem;
        }
        /* Style for selectbox to match other inputs */
        .stSelectbox > div > select {
            border: 1px solid #d1d5db;
            border-radius: 0.375rem;
            padding: 0.5rem;
        }
        /* Style for sliders to ensure consistent appearance */
        .stSlider > div > div {
            border: 1px solid #d1d5db;
            border-radius: 0.375rem;
            padding: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h2 style='text-align:center; margin:0 0 .5rem 0;'>"
        "📌 Baseline &nbsp;" # Emoji for emphasis
        "</h2>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p style='text-align:center; font-size:1rem; color:#6c757d; margin-bottom:1rem;'>
        💡 Please complete or update the following personal information to personalize your 30-day plan!
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.container(): # Use a container for better organization
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True) # Apply card styling

        st.subheader("🆔 Identity")
        # --- Gender ---
        current_gender = st.session_state.get("gender", "Male") # Default to 'Male'
        gender_options = ["Male", "Female"]
        if current_gender not in gender_options: current_gender = "Male" # Fallback
        gender = st.selectbox("⚧️ Gender", gender_options, index=gender_options.index(current_gender))

        # --- Age ---
        current_age = st.session_state.get("age", 25) # Default to 25
        age = st.slider("🎂 Age (yrs)", 10, 80, value=current_age)

        st.subheader("📐 Measurements")
        # --- Height ---
        current_height_cm = st.session_state.get("height", 170.0)
        if not isinstance(current_height_cm, (int, float)): current_height_cm = 170.0 # Ensure numeric, default to 170cm
        height_m = current_height_cm / 100 # Convert cm to meters for slider display
        height = st.slider("📏 Height (m)", 1.0, 2.2, value=height_m, step=0.01)

        # --- Weight ---
        current_weight = st.session_state.get("weight", 70.0) # Default to 70kg
        weight = st.slider("⚖️ Weight (kg)", 30.0, 200.0, value=current_weight, step=0.1)

        st.subheader("🏠 Lifestyle")
        # --- Family History ---
        current_family = st.session_state.get("family_history_with_overweight", "yes")
        family_options = ["yes", "no"]
        if current_family not in family_options: current_family = "yes" # Fallback
        family = st.selectbox("🧑‍🧑‍🧒 Family history of overweight", family_options, index=family_options.index(current_family))

        # --- FAVC (Frequent High-Calorie Food) ---
        current_favc = st.session_state.get("favc", "yes")
        favc_options = ["yes", "no"]
        if current_favc not in favc_options: current_favc = "yes" # Fallback
        favc = st.selectbox("🍿 Frequent high-cal food", favc_options, index=favc_options.index(current_favc))

        # --- FCVC (Vegetable Servings) ---
        current_fcvc = st.session_state.get("fcvc", 2)
        fcvc = st.slider("🥗 Veg servings / week", 0, 7, value=current_fcvc)

        # --- NCP (Meals per Day) ---
        current_ncp = st.session_state.get("ncp", 3)
        ncp = st.slider("🍽️ Meals / day", 1, 5, value=current_ncp)

        # --- CAEC (Snacking Habits) ---
        current_caec_raw = st.session_state.get("caec")
        # Normalize the value from session state: trim whitespace and handle potential non-string types
        if current_caec_raw is not None:
            current_caec = str(current_caec_raw).strip()
        else:
            current_caec = "Sometimes" # Default if not found or invalid
        caec_options = ["Always", "Frequently", "Sometimes"]
        if current_caec not in caec_options: # Ensure value exists in options, otherwise use default
            current_caec = "Sometimes"
        caec = st.selectbox("🍪 Snacking", caec_options, index=caec_options.index(current_caec))

        # --- SMOKE ---
        current_smoke = st.session_state.get("smoke", "no")
        smoke_options = ["yes", "no"]
        if current_smoke not in smoke_options: current_smoke = "no" # Fallback
        smoke = st.selectbox("🚬 Smoking", smoke_options, index=smoke_options.index(current_smoke))

        # --- CH2O (Water Intake) ---
        current_ch2o = st.session_state.get("ch2o", 2.0)
        ch2o = st.slider("💧 Water (L/day)", 0.5, 5.0, value=current_ch2o, step=0.1)

        # --- SCC (Sugary Drinks Consumption) ---
        current_scc = st.session_state.get("scc", "no")
        scc_options = ["yes", "no"]
        if current_scc not in scc_options: current_scc = "no" # Fallback
        scc = st.selectbox("🥤 Sugary drinks", scc_options, index=scc_options.index(current_scc))

        st.subheader("🏃 Activity & Transport")
        # --- FAF (Physical Activity Frequency) ---
        current_faf = st.session_state.get("faf", 2)
        faf = st.slider("🏋️ Exercise sessions / week", 0, 7, value=current_faf)

        # --- TUE (Time Using Electronic Devices) ---
        current_tue = st.session_state.get("tue", 3)
        tue = st.slider("📺 Screen time (h/day)", 0, 12, value=current_tue)

        # --- CALC (Alcohol Consumption) ---
        current_calc_raw = st.session_state.get("calc")
        # Normalize the value from session state
        if current_calc_raw is not None:
            current_calc = str(current_calc_raw).strip()
        else:
            current_calc = "No" # Default if not found or invalid
        calc_options = ["No", "Sometimes", "Frequently"]
        if current_calc not in calc_options: # Ensure value exists in options, otherwise use default
            current_calc = "No"
        calc = st.selectbox("🍷 Alcohol", calc_options, index=calc_options.index(current_calc))

        # --- MTRANS (Transportation) ---
        current_mtrans_raw = st.session_state.get("mtrans")
        # Normalize the value from session state
        if current_mtrans_raw is not None:
            current_mtrans = str(current_mtrans_raw).strip()
        else:
            current_mtrans = "Public" # Default if not found or invalid
        # Handle the old value 'Public_Transportation' if it exists in session state
        if current_mtrans == "Public_Transportation":
            current_mtrans = "Public"
        mtrans_options = ["Walking", "Bike", "Public", "Car", "Motorbike"]
        if current_mtrans not in mtrans_options: # Ensure value exists in options, otherwise use default
            current_mtrans = "Public"
        mtrans = st.selectbox("🚲 Transport", mtrans_options, index=mtrans_options.index(current_mtrans))

        st.markdown('</div>', unsafe_allow_html=True) # Close card div

    st.markdown("---")
    st.caption("💡 Hover or click to adjust values.")

    # --- Session State Update and Rerun Logic ---
    # Check if any of the sidebar inputs have changed their value
    state_changed = False
    if st.session_state.get("gender") != gender: state_changed = True
    if st.session_state.get("age") != age: state_changed = True
    if st.session_state.get("height") != height * 100: state_changed = True # Compare in cm
    if st.session_state.get("weight") != weight: state_changed = True
    if st.session_state.get("family_history_with_overweight") != family: state_changed = True
    if st.session_state.get("favc") != favc: state_changed = True
    if st.session_state.get("fcvc") != fcvc: state_changed = True
    if st.session_state.get("ncp") != ncp: state_changed = True
    if st.session_state.get("caec") != caec: state_changed = True # Use the standardized 'caec'
    if st.session_state.get("smoke") != smoke: state_changed = True
    if st.session_state.get("ch2o") != ch2o: state_changed = True
    if st.session_state.get("scc") != scc: state_changed = True
    if st.session_state.get("faf") != faf: state_changed = True
    if st.session_state.get("tue") != tue: state_changed = True
    if st.session_state.get("calc") != calc: state_changed = True # Use the standardized 'calc'
    if st.session_state.get("mtrans") != mtrans: state_changed = True # Use the standardized 'mtrans'

    if state_changed:
        st.session_state.update({
            "gender": gender,
            "age": age,
            "height": height * 100,  # Store height in cm
            "weight": weight,
            "family_history_with_overweight": family,
            "favc": favc,
            "fcvc": fcvc,
            "ncp": ncp,
            "caec": caec, # Store the standardized 'caec'
            "smoke": smoke,
            "ch2o": ch2o,
            "scc": scc,
            "faf": faf,
            "tue": tue,
            "calc": calc, # Store the standardized 'calc'
            "mtrans": mtrans # Store the standardized 'mtrans'
        })
        st.rerun() # Rerun the app to reflect changes in the main content

# ---------- Initialize selected_scenarios ----------
if "selected_scenarios" not in st.session_state:
    st.session_state["selected_scenarios"] = ["Baseline"]
    logging.info("Initialized selected_scenarios with ['Baseline']")

# ---------- Build base_df AFTER sidebar widgets to ensure latest session state values are used ----------
base_df = pd.DataFrame([{
    "Gender": st.session_state.get("gender", "Male"),
    "Age": st.session_state.get("age", 25),
    "Height": st.session_state.get("height", 170.0) / 100, # Convert cm back to meters for model input
    "Weight": st.session_state.get("weight", 70.0),
    "family_history_with_overweight": st.session_state.get("family_history_with_overweight", "yes"),
    "FAVC": st.session_state.get("favc", "yes"),
    "FCVC": st.session_state.get("fcvc", 2),
    "NCP": st.session_state.get("ncp", 3),
    "CAEC": st.session_state.get("caec", "Sometimes"), # Use the potentially corrected value
    "SMOKE": st.session_state.get("smoke", "no"),
    "CH2O": st.session_state.get("ch2o", 2.0),
    "SCC": st.session_state.get("scc", "no"),
    "FAF": st.session_state.get("faf", 2),
    "TUE": st.session_state.get("tue", 3),
    "CALC": st.session_state.get("calc", "No"), # Use the potentially corrected value
    "MTRANS": st.session_state.get("mtrans", "Public"), # Use the potentially corrected value
}])[feature_order] # Ensure columns are in the correct order for the model

# ---------- Lifestyle Tweaks Section ----------
st.subheader("Tweak Your Habits")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        extra_water = st.slider("💧 Extra water intake (L/day)", -4.0, 4.0, 0.0, 0.1, help="Adjust daily water intake relative to current level")
        if abs(extra_water) > 3.0:
            st.warning(f"⚠️ {extra_water:+.1f} L/day extra water is significant! Ensure hydration balance.")
        extra_ex = st.slider("🏋️ Extra workouts / week (sessions)", -7, 7, 0)
        if abs(extra_ex) > 5:
            st.warning(f"⚠️ {extra_ex} extra sessions/week may over-train.")
        veg_add = st.slider("🥗 Extra veg servings / week", -7, 7, 0)
        no_drink = st.checkbox("❌ Quit sugary drinks")
    with col2:
        sleep_add = st.slider("🌙 Extra sleep hrs / week", -14, 14, 0)
        if abs(sleep_add) > 10:
            st.warning("⚠️ Large sleep changes can disrupt rhythm.")
        alc_red = st.slider("🍻 Reduce alcohol days / week (days)", -7, 7, 0)
        screen_red = st.slider("🖥️ Reduce screen hrs / week (hours)", -21, 21, 0)
        if abs(screen_red) > 14:
            st.warning("⚠️ Cutting > 14 hrs/week screen time is ambitious.")
        quit_smoke = st.checkbox("🚭 Quit smoking")

# Dictionary to hold lifestyle adjustments
delta = {
    "extra_water": extra_water,
    "extra_ex": extra_ex,
    "veg_add": veg_add,
    "no_drink": no_drink,
    "sleep_add": sleep_add,
    "alc_red": alc_red,
    "screen_red": screen_red,
    "quit_smoke": quit_smoke,
}

# ---------- Scenario Manager ----------
st.subheader("💾 Scenario Manager")

def handle_save():
    """Callback to handle saving a new scenario."""
    if new_name.strip():
        st.session_state.setdefault("scenarios", {})[new_name.strip()] = delta
        current_selected = st.session_state.get("selected_scenarios", ["Baseline"])
        if new_name.strip() not in current_selected:
            current_selected.append(new_name.strip())
            st.session_state["selected_scenarios"] = current_selected
        logging.info(f"Saved scenario: {new_name.strip()}, selected_scenarios: {current_selected}")
        st.success(f"Scenario '{new_name.strip()}' saved!")
        st.session_state["update_trigger"] = np.random.rand()  # Force update
    else:
        st.warning("Please enter a name for the scenario before saving.")

def handle_delete():
    """Callback to handle deleting a scenario."""
    if to_del:
        st.session_state["scenarios"].pop(to_del)
        current_selected = st.session_state.get("selected_scenarios", ["Baseline"])
        if to_del in current_selected:
            current_selected.remove(to_del)
            st.session_state["selected_scenarios"] = current_selected
        logging.info(f"Deleted scenario: {to_del}, selected_scenarios: {current_selected}")
        st.success(f"Scenario '{to_del}' deleted!")
        st.session_state["update_trigger"] = np.random.rand()  # Force update

def handle_clear_all():
    """Callback to handle clearing all scenarios."""
    st.session_state["scenarios"] = {}
    st.session_state["selected_scenarios"] = ["Baseline"]
    logging.info("Cleared all scenarios, selected_scenarios: ['Baseline']")
    st.success("All scenarios cleared!")
    st.session_state["update_trigger"] = np.random.rand()  # Force update

# Initialize update_trigger if not present
if "update_trigger" not in st.session_state:
    st.session_state["update_trigger"] = np.random.rand()

save_col1, save_col2 = st.columns([3, 1])
with save_col1:
    new_name = st.text_input(
        "Save current settings as",
        f"Scenario {len(st.session_state.get('scenarios', {}))+1}",
        label_visibility="collapsed"
    )
with save_col2:
    st.button("💾 Save", type="primary", use_container_width=True, on_click=handle_save)

# Display existing scenarios and provide delete functionality
if st.session_state.get("scenarios"):
    del_col1, del_col2 = st.columns([3, 1])
    with del_col1:
        scenario_names = list(st.session_state["scenarios"].keys())
        if scenario_names:
            to_del = st.selectbox(
                "Choose scenario to delete",
                scenario_names,
                label_visibility="collapsed"
            )
        else:
            st.info("No scenarios saved yet.")
            to_del = None
    with del_col2:
        if scenario_names:
            st.button("🗑️ Delete", use_container_width=True, on_click=handle_delete)

# Button to clear all saved scenarios
if st.session_state.get("scenarios"):
    st.button("⚠️ Clear ALL scenarios", use_container_width=True, on_click=handle_clear_all)

# ---------- 30-Day Weight Projection ----------
st.header("📈 30-Day Weight Projection")

with st.expander("📊 Why is the line wavy?", expanded=False):
    st.markdown(
        """
        - Daily ±15 kcal random fluctuation (NEAT, digestion, hydration)
        - Weekend vs weekday activity difference
        - Real biological noise keeps the curve realistic
        """
    )

# Prepare data for plotting
plot_data = {"Day": list(range(31))} # Days from 0 to 30
# Calculate baseline projection
baseline, _ = predict_30d(base_df, {k: 0 for k in delta}) # Delta is all zeros for baseline
plot_data["Baseline"] = baseline

# Calculate projections for each saved scenario
for sc_name, d in st.session_state.get("scenarios", {}).items():
    # Ensure the delta dictionary is properly formed, provide defaults if missing keys
    scenario_delta = {
        "extra_water": d.get("extra_water", 0),
        "extra_ex": d.get("extra_ex", 0),
        "veg_add": d.get("veg_add", 0),
        "no_drink": d.get("no_drink", False),
        "sleep_add": d.get("sleep_add", 0),
        "alc_red": d.get("alc_red", 0),
        "screen_red": d.get("screen_red", 0),
        "quit_smoke": d.get("quit_smoke", False),
    }
    plot_data[sc_name], _ = predict_30d(base_df, scenario_delta)

# Convert to DataFrame for Altair plotting
df_plot = pd.DataFrame(plot_data).melt("Day", var_name="Scenario", value_name="Weight (kg)")

# Multiselect for choosing which scenarios to display
all_scenarios = ["Baseline"] + list(st.session_state.get("scenarios", {}).keys())
# Filter selected to only include existing scenarios
st.session_state["selected_scenarios"] = [s for s in st.session_state["selected_scenarios"] if s in all_scenarios]
# Use a dynamic key to force re-rendering of multiselect
multiselect_key = f"scenario_select_{len(all_scenarios)}_{hash(str(all_scenarios))}_{st.session_state['update_trigger']}"
selected = st.multiselect(
    "Choose scenarios to display",
    all_scenarios,
    default=st.session_state["selected_scenarios"].copy(),  # Use copy to avoid modifying default
    key=multiselect_key
)
st.session_state["selected_scenarios"] = selected # Save selection to session state
logging.info(f"Selected scenarios updated: {selected}")

# Filter data based on user selection
df_filtered = df_plot[df_plot["Scenario"].isin(selected)]

# Create the Altair chart for weight projection
chart = (
    alt.Chart(df_filtered)
    .mark_line(strokeWidth=3, point=True) # Line with points
    .encode(
        x=alt.X("Day:O", title="Day", axis=alt.Axis(labelAngle=0)), # Day on X-axis (Ordinal)
        y=alt.Y("Weight (kg):Q", scale=alt.Scale(zero=False)), # Weight on Y-axis (Quantitative, not starting from zero)
        color=alt.Color("Scenario:N", scale=alt.Scale(scheme="category20")), # Color by Scenario (Nominal)
        tooltip=[ # Tooltip for interactivity
            alt.Tooltip("Scenario:N", title="Scenario"),
            alt.Tooltip("Weight (kg):Q", title="Weight", format=".2f"),
            alt.Tooltip("Day:O", title="Day"),
        ],
    )
    .properties(height=450, title="Weight Projection Over 30 Days") # Set chart height and title
    .interactive() # Make chart interactive (zoom/pan)
)
st.altair_chart(chart, use_container_width=True)

# ---------- Scenario Summary Table ----------
st.subheader("📊 Scenario Summary")
if st.session_state.get("scenarios"): # Only show if scenarios exist
    all_data = {"Baseline": baseline} # Start with baseline
    # Add all saved scenarios' weight lists
    for sc_name, d in st.session_state["scenarios"].items():
        scenario_delta = { # Re-ensure delta is correctly formed for each scenario
            "extra_water": d.get("extra_water", 0), "extra_ex": d.get("extra_ex", 0),
            "veg_add": d.get("veg_add", 0), "no_drink": d.get("no_drink", False),
            "sleep_add": d.get("sleep_add", 0), "alc_red": d.get("alc_red", 0),
            "screen_red": d.get("screen_red", 0), "quit_smoke": d.get("quit_smoke", False),
        }
        all_data[sc_name] = predict_30d(base_df, scenario_delta)[0]

    # Slider to select which day's summary to view
    slider_day = st.slider("Drag to view any day's summary", 0, 30, 30) # Default to last day (Day 30)

    summary_data = []
    baseline_weight_at_slider_day = baseline[slider_day] # Baseline weight on the selected day

    # Generate summary row for each scenario
    for name, w_list in all_data.items():
        w_day = w_list[slider_day] # Weight on the selected day for this scenario
        delta_w = w_day - baseline_weight_at_slider_day # Change in weight compared to baseline
        
        # Determine trend direction
        trend = "⬇️ Decrease" if delta_w < -0.1 else ("⬆️ Increase" if delta_w > 0.1 else "➡️ Stable")
        
        # Calculate BMI and level for the selected day
        bmi_day = w_day / (base_df["Height"].iat[0] ** 2)
        level_day = bmi_level(bmi_day)
        
        summary_data.append({
            "Scenario": name,
            f"Weight Day {slider_day}": f"{w_day:.2f} kg",
            "Δ Weight": f"{delta_w:+.2f} kg",
            "Trend": trend,
            "Obesity Level": level_day,
        })
    
    # Display the summary in a dataframe
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

# ---------- Current Obesity Level Prediction ----------
st.subheader("Current Obesity Level")
try:
    # Ensure base_df is valid before prediction
    if not base_df.empty:
        # Predict probabilities for the current baseline
        # predict_proba returns an array of probability arrays, one for each sample (here, only 1 sample)
        proba = model.predict_proba(base_df)[0]
        predicted_class_index = np.argmax(proba) # Get the index of the class with highest probability
        
        # Decode the predicted class index back to the original label string using the label encoder
        level = le.inverse_transform([predicted_class_index])[0]
        st.success(f"Your current predicted obesity level is: **{level}**")
    else:
        st.warning("Cannot predict obesity level: Baseline data is missing or invalid.")
except Exception as e:
    st.error(f"Error during obesity level prediction: {e}")
    logging.error(f"Obesity level prediction failed: {e}")

# ---------- Backup & Restore Functionality ----------
st.subheader("💾 Backup & Restore Your Scenarios")

# Export Button
if st.session_state.get("scenarios"): # Only show if there are scenarios to export
    try:
        # Convert scenarios dictionary to JSON string with indentation for readability
        json_str = json.dumps(st.session_state["scenarios"], indent=2)
        st.download_button(
            label="📥 Export Scenarios (JSON)",
            data=json_str,
            file_name="30d_body_planner_scenarios.json",
            mime="application/json",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error during scenario export: {e}")
        logging.error(f"Scenario export failed: {e}")

# Import File Uploader
uploaded = st.file_uploader("📤 Import Scenarios (JSON)", type=["json"])
if uploaded:
    try:
        content = uploaded.read() # Read the uploaded file content
        data_str = content.decode('utf-8') # Decode bytes to string (assuming UTF-8 encoding)
        imported = json.loads(data_str) # Parse the JSON string into a Python dictionary

        # Validate the imported data structure
        if isinstance(imported, dict):
            # Optional: Add more robust validation for the structure of scenarios if needed
            st.session_state["scenarios"] = imported # Replace current scenarios with imported ones
            # Automatically select all imported scenarios for display
            st.session_state["selected_scenarios"] = ["Baseline"] + list(imported.keys())
            st.success("✅ Scenarios imported successfully!")
            logging.info("Imported scenarios successfully, selected_scenarios: {}".format(st.session_state["selected_scenarios"]))
            st.session_state["update_trigger"] = np.random.rand()  # Force update
        else:
            st.error("❌ Invalid JSON format. Expected a dictionary of scenarios.")
            logging.error("Invalid JSON format during import")
    except json.JSONDecodeError:
        st.error("❌ Failed to parse JSON. Please ensure the file is a valid JSON document.")
        logging.error("JSON parsing failed during import")
    except UnicodeDecodeError:
        st.error("❌ Failed to decode file content. Please ensure the file is UTF-8 encoded.")
        logging.error("Unicode decode error during import")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred during import: {e}")
        logging.error(f"Unexpected error during import: {e}")