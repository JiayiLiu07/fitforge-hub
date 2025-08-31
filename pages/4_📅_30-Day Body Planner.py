# pages/6_📅_30-Day Body Planner.py
# =========================================================
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import joblib
import json

# ---------- 0. Page Config ----------
st.set_page_config(
    page_title="30-Day Body Planner",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_PATH = "models/obesity_xgb.pkl"
numerical = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]
categorical = ["Gender", "family_history_with_overweight", "FAVC", "CAEC",
               "SMOKE", "SCC", "CALC", "MTRANS"]
feature_order = numerical + categorical

@st.cache_resource
def load_model_and_encoder():
    loaded = joblib.load(MODEL_PATH)
    return loaded["model"], loaded["le"]

model, le = load_model_and_encoder()

# ---------- WHO BMI ----------
def bmi_level(bmi):
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

def tdee(w, h_cm, age, gender, activity):
    bmr = (10 * w) + (6.25 * h_cm) - (5 * age) + (5 if gender == "Male" else -161)
    return bmr * activity

def predict_30d(base_row, delta, seed=42):
    rng = np.random.default_rng(seed)
    w0 = base_row["Weight"].iat[0]
    h_cm = base_row["Height"].iat[0] * 100
    age = base_row["Age"].iat[0]
    gender = base_row["Gender"].iat[0]
    activity = 1.2 + base_row["FAF"].iat[0] * 0.075

    daily_deficit = (
        delta["steps"] * 0.04 +
        delta["extra_ex"] * 150 +
        delta["veg_add"] * 15 +
        (150 if delta["no_drink"] else 0) +
        delta["sleep_add"] * 50 +
        delta["alc_red"] * 100 +
        delta["screen_red"] * 30 +
        delta["quit_smoke"] * 100
    )

    weights = [w0]
    for day in range(1, 31):
        factor = 1.0 if day % 7 < 5 else 0.9
        real_deficit = daily_deficit * factor + rng.normal(0, 15)
        w_new = weights[-1] - real_deficit / 7700
        w_new = max(w_new, 25)
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

# ---------- Sidebar (always first, defines base_df) ----------
with st.sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            padding-top: 0;
        }
        .sidebar-card {
            background: #ffffff10;
            border-radius: 8px;
            padding: .8rem .6rem .6rem .8rem;
            margin-bottom: .6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h2 style='text-align:center; margin:0 0 .5rem 0;'>"
        "📌 Baseline &nbsp;"
        "</h2>",
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)

        st.subheader("🆔 Identity")
        gender = st.selectbox("⚧️Gender", ["Male", "Female"])
        age = st.slider("🎂Age (yrs)", 10, 80, 25)

        st.subheader("📐 Measurements")
        height = st.slider("📏Height (m)", 1.0, 2.2, 1.70, 0.01)
        weight = st.slider("⚖️ Weight (kg)", 30.0, 200.0, 70.0, 0.1)

        st.subheader("🏠 Lifestyle")
        family = st.selectbox("🧑‍🧑‍🧒Family history overweight", ["yes", "no"])
        favc = st.selectbox("🍿Frequent high-cal food", ["yes", "no"])
        fcvc = st.slider("🥗 Veg servings / week", 0, 7, 2)
        ncp = st.slider("🍽️ Meals / day", 1, 5, 3)
        caec = st.selectbox("🍪 Snacking", ["Always", "Frequently", "Sometimes"])
        smoke = st.selectbox("🚬 Smoking", ["yes", "no"])
        ch2o = st.slider("💧 Water (L/day)", 0.5, 5.0, 2.0, 0.1)
        scc = st.selectbox("🥤 Sugary drinks", ["yes", "no"])

        st.subheader("🏃 Activity & Transport")
        faf = st.slider("🏋️ Exercise sessions / week", 0, 7, 2)
        tue = st.slider("📺 Screen time (h/day)", 0, 12, 3)
        calc = st.selectbox("🍷 Alcohol", ["no", "Sometimes", "Frequently"])
        mtrans = st.selectbox("🚲 Transport", ["Walking", "Bike", "Public", "Car", "Motorbike"])

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("💡 Hover or click to adjust values.")

# build base_df AFTER sidebar widgets
base_df = pd.DataFrame([{
    "Gender": gender, "Age": age, "Height": height, "Weight": weight,
    "family_history_with_overweight": family, "FAVC": favc, "FCVC": fcvc,
    "NCP": ncp, "CAEC": caec, "SMOKE": smoke, "CH2O": ch2o,
    "SCC": scc, "FAF": faf, "TUE": tue, "CALC": calc, "MTRANS": mtrans,
}])[feature_order]

# ---------- Lifestyle Tweaks ----------
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        steps_manual = st.slider("Extra steps / day", -8000, 80000, 0, 500, help="≈ 2 000 steps ≈ 1 km")
        if abs(steps_manual) > 20000:
            st.warning(f"⚠️ {steps_manual:,} steps/day is extreme! Risk of injury.")
        extra_ex = st.slider("Extra workouts / week (sessions)", -7, 7, 0)
        if abs(extra_ex) > 5:
            st.warning(f"⚠️ {extra_ex} extra sessions/week may over-train.")
        veg_add = st.slider("Extra veg servings / week", -7, 7, 0)
        no_drink = st.checkbox("Quit sugary drinks")
    with col2:
        sleep_add = st.slider("Extra sleep hrs / week", -14, 14, 0)
        if abs(sleep_add) > 10:
            st.warning("⚠️ Large sleep changes can disrupt rhythm.")
        alc_red = st.slider("Reduce alcohol days / week (days)", -7, 7, 0)
        screen_red = st.slider("Reduce screen hrs / week (hours)", -21, 21, 0)
        if abs(screen_red) > 14:
            st.warning("⚠️ Cutting > 14 hrs/week screen time is ambitious.")
        quit_smoke = st.checkbox("Quit smoking")

delta = {
    "steps": steps_manual,
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

save_col1, save_col2 = st.columns([3, 1])
with save_col1:
    new_name = st.text_input(
        "Save current settings as",
        f"Scenario {len(st.session_state.get('scenarios', {}))+1}",
        label_visibility="collapsed"
    )
with save_col2:
    if st.button("💾 Save", type="primary", use_container_width=True):
        st.session_state.setdefault("scenarios", {})[new_name] = delta
        st.rerun()

if st.session_state.get("scenarios"):
    del_col1, del_col2 = st.columns([3, 1])
    with del_col1:
        to_del = st.selectbox(
            "Choose scenario to delete",
            list(st.session_state["scenarios"].keys()),
            label_visibility="collapsed"
        )
    with del_col2:
        if st.button("🗑️ Delete", use_container_width=True):
            st.session_state["scenarios"].pop(to_del, None)
            st.rerun()

if st.session_state.get("scenarios"):
    if st.button("⚠️ Clear ALL scenarios", use_container_width=True):
        st.session_state["scenarios"] = {}
        st.rerun()

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

plot_data = {"Day": list(range(31))}
baseline, _ = predict_30d(base_df, {k: 0 for k in delta})
plot_data["Baseline"] = baseline

for sc_name, d in st.session_state.get("scenarios", {}).items():
    plot_data[sc_name], _ = predict_30d(base_df, d)

df_plot = pd.DataFrame(plot_data).melt("Day", var_name="Scenario", value_name="Weight (kg)")

all_scenarios = ["Baseline"] + list(st.session_state.get("scenarios", {}).keys())
selected = st.multiselect("Choose scenarios to display", all_scenarios, default=all_scenarios)
df_filtered = df_plot[df_plot["Scenario"].isin(selected)]

chart = (
    alt.Chart(df_filtered)
    .mark_line(strokeWidth=3, point=True)
    .encode(
        x=alt.X("Day:O", title="Day", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Weight (kg):Q", scale=alt.Scale(zero=False)),
        color=alt.Color("Scenario:N", scale=alt.Scale(scheme="category20")),
        tooltip=[
            alt.Tooltip("Scenario:N", title="Scenario"),
            alt.Tooltip("Weight (kg):Q", title="Weight", format=".2f"),
            alt.Tooltip("Day:O", title="Day"),
        ],
    )
    .properties(height=450)
)
st.altair_chart(chart, use_container_width=True)

# ---------- Scenario Summary ----------
if st.session_state.get("scenarios"):
    st.subheader("📊 Scenario Summary")
    all_data = {"Baseline": baseline}
    all_data.update({k: predict_30d(base_df, v)[0] for k, v in st.session_state["scenarios"].items()})
    slider_day = st.slider("Drag to view any day", 0, 30, 30)

    summary = []
    for name, w_list in all_data.items():
        w_day = w_list[slider_day]
        delta_w = w_day - baseline[slider_day]
        trend = "⬇️ Decrease" if delta_w < -0.1 else ("⬆️ Increase" if delta_w > 0.1 else "➡️ Stable")
        bmi_day = w_day / (base_df["Height"].iat[0] ** 2)
        summary.append({
            "Scenario": name,
            f"Weight Day {slider_day}": f"{w_day:.2f} kg",
            "Δ Weight": f"{delta_w:+.2f} kg",
            "Trend": trend,
            "Obesity Level": bmi_level(bmi_day),
        })
    st.dataframe(pd.DataFrame(summary).set_index("Scenario"))

# ---------- Current Level ----------
proba = model.predict_proba(base_df)[0]
level = le.inverse_transform([np.argmax(proba)])[0]
st.success(f"Current obesity level: **{level}**")



# ---------- Backup & Restore ----------
st.subheader("💾 Backup & Restore")

# 导出
if st.session_state.get("scenarios"):
    json_str = json.dumps(st.session_state["scenarios"])
    st.download_button(
        label="📥 Export Scenarios (JSON)",
        data=json_str,
        file_name="30d_body_planner_scenarios.json",
        mime="application/json",
        use_container_width=True,
    )

# 导入
uploaded = st.file_uploader("📤 Import Scenarios (JSON)", type=["json"])
if uploaded:
    try:
        imported = json.load(uploaded)
        if isinstance(imported, dict):
            st.session_state["scenarios"] = imported
            st.success("✅ Scenarios imported successfully!")
            st.rerun()
        else:
            st.error("❌ Invalid JSON format.")
    except Exception as e:
        st.error(f"❌ Import failed: {e}")