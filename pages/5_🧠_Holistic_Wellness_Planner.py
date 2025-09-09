import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from openai import OpenAI
import logging
import uuid
import random
import time
import json



# --- Configure Logging ---
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define TIPS dictionary ---
TIPS = {
    "Reduce Stress": [
        "Practice 5–10 minutes of mindful breathing daily. Inhale deeply for 4 counts, hold for 4, exhale for 6. ✨",
        "Incorporate a short walk outdoors each day. Sunlight and fresh air can significantly boost your mood. 🌳",
        "Listen to calming music for 15–20 minutes. Focus on the rhythm and melody to unwind. 🎶",
        "Engage in a brief journaling session. Write down your thoughts and feelings to process them. ✍️",
        "Try a simple stretching routine to release physical tension. Focus on your breath during each stretch. 🧘‍♀️",
        "Spend 10 minutes in nature, even if it's just looking out a window. Connect with the natural world. 🌿",
        "Practice gratitude by listing three things you are thankful for each day. It shifts your focus to the positive. 🙏",
        "Limit exposure to stressful news or social media for an hour before bedtime. 📵",
        "Deepen your stretches during yoga or everyday movements. Hold each stretch slightly longer, focusing on releasing tension. 😌",
        "Engage in a creative activity for at least 15 minutes, like drawing, painting, or doodling. Let your imagination flow. 🎨",
        "Take a warm bath or shower to relax your muscles and clear your mind. 🚿",
        "Spend time with loved ones. Social connection can be a powerful stress reliever. 🤗",
        "Engage in light physical activity, like walking or stretching, to release endorphins. 🚶‍♀️",
        "Practice progressive muscle relaxation: tense and release different muscle groups to reduce physical tension. 💪",
        "Focus on one task at a time to avoid feeling overwhelmed. Mindfulness can help here. 🎯"
    ],
    "Improve Sleep": [
        "Establish a consistent sleep schedule, going to bed and waking up around the same time every day, even on weekends. ⏰",
        "Create a relaxing bedtime routine: take a warm bath, read a book, or listen to calming music for at least 30 minutes before sleep. 🛀📚🎶",
        "Ensure your bedroom is dark, quiet, and cool. Use blackout curtains, earplugs, or a white noise machine if needed. 🌙🔇",
        "Avoid caffeine and heavy meals close to bedtime. Limit screen time for at least an hour before sleep. ☕️📱❌",
        "Consider gentle stretching or a short meditation to calm your mind before sleep. Focus on deep, slow breaths. 🧘‍♂️🌬️",
        "Expose yourself to natural light during the day, especially in the morning, to regulate your body's natural sleep-wake cycle. ☀️",
        "If you can't fall asleep after 20 minutes, get out of bed and do a quiet, relaxing activity until you feel sleepy, then return to bed. 🚶‍♀️💤",
        "Avoid long naps during the day, especially late in the afternoon, as they can interfere with nighttime sleep. 😴❌",
        "Practice progressive muscle relaxation by tensing and releasing different muscle groups to promote physical relaxation. 💪➡️😌",
        "Journal your worries or to-do list for the next day before bed. This can help clear your mind and reduce rumination. 📝",
        "Limit fluid intake in the hour before bed to minimize nighttime awakenings for bathroom trips. 🚰❌",
        "Make your bedroom a sanctuary for sleep. Remove electronics and keep it tidy and calming. 🛌",
        "If you often wake up in the middle of the night, try reading a physical book under dim light until you feel sleepy again. 📖",
        "Gentle activities like light stretching or a warm, non-caffeinated herbal tea can signal to your body that it's time to wind down. 🍵"
    ],
    "Increase Mindfulness": [
        "Start your day with 5–10 minutes of focused breathing. Pay attention to the sensation of your breath entering and leaving your body. 🌬️",
        "Practice mindful eating. Pay full attention to the taste, texture, and smell of your food. Chew slowly and savor each bite. 🍎",
        "Engage in a mindful walking meditation. Focus on the sensation of your feet touching the ground and the rhythm of your steps. 🚶‍♂️",
        "When you feel overwhelmed, pause for a moment. Take three deep breaths and notice your surroundings without judgment. 🧘‍♀️",
        "Practice mindful listening. When someone is speaking, give them your full attention without planning your response. 👂",
        "Incorporate mindful moments into routine activities like brushing your teeth or washing dishes. Focus on the sensations. 🚿",
        "Spend time observing nature without distraction. Notice the details of leaves, clouds, or sounds. 🌳☁️",
        "Try a body scan meditation. Bring your awareness to each part of your body, noticing any sensations. 🦵👣",
        "When experiencing emotions, acknowledge them without judgment. Notice where you feel them in your body. ❤️",
        "Practice single-tasking. Focus on completing one task at a time with your full attention. 🎯",
        "Take 60 seconds to observe your breath, noticing its natural rhythm without trying to change it. ⏳",
        "When your mind wanders, gently guide your attention back to your anchor (like breath or bodily sensations). 🧭",
        "During conversations, focus solely on understanding the speaker, rather than formulating your reply. 🗣️",
        "Mindfully appreciate everyday sensory experiences, like the warmth of a cup or the taste of your coffee. ☕️"
    ],
    "Increase Water Intake": [
        "Carry a reusable water bottle with you everywhere and sip from it throughout the day. 💧",
        "Set reminders on your phone or use a smart water bottle to prompt you to drink every hour. ⏰",
        "Drink a glass of water before each meal. This can also aid digestion and satiety. 🍽️",
        "Infuse your water with fruits like lemon, cucumber, or berries for added flavor and a refreshing twist. 🍋🥒",
        "Replace sugary drinks or sodas with water. This is a significant step towards better hydration and health. 🥤❌",
        "Start your day by drinking a large glass of water immediately after waking up. Hydrate your body after a night's sleep. 🌅",
        "Make drinking water a part of your routine. For example, drink a glass every time you take a break or switch tasks. ☕️➡️💧",
        "Track your water intake using an app or a simple tally. Visualizing your progress can be motivating. 📊",
        "Drink water while commuting or during your work breaks. It’s an easy way to increase intake without disruption. 🚗🚌",
        "Enjoy sparkling water or herbal teas if you prefer something other than plain water, ensuring they are unsweetened. 🥂🍵",
        "Add mint leaves or a slice of orange to your water for a natural flavor boost. 🍊",
        "Aim to finish your first liter of water before noon. 🕛",
        "Keep a water bottle at your desk or by your side to encourage regular sips. 🗄️"
    ],
    "Eat More Vegetables": [
        "Add a serving of vegetables to every meal. For breakfast, try spinach in your eggs or a side of tomatoes. 🍳🍅",
        "Include at least two different types of vegetables in your main meals (lunch and dinner). Aim for variety in color and texture. 🥦🥕",
        "Sneak vegetables into dishes you already love. Finely chopped carrots or zucchini can disappear into pasta sauces or casseroles. 🍝",
        "Snack on raw vegetables like carrots, celery, or bell peppers with hummus or a healthy dip. 🥕🫙",
        "Experiment with new vegetable recipes weekly. Explore different cooking methods like roasting, steaming, or stir-frying. 🍄🌶️",
        "Make salads a regular part of your diet, packing them with a variety of greens and other vegetables. 🥗",
        "Blend vegetables into smoothies. Spinach or kale can be masked by fruits like berries or bananas. 🍓🥬",
        "Roast a large batch of mixed vegetables at the beginning of the week to easily add to meals. 🍠🍆",
        "Try vegetable-based soups or stews for a comforting and nutrient-rich meal. 🥣",
        "When dining out, choose dishes that feature vegetables prominently or order an extra side of vegetables. 🍽️",
        "Add avocado to your toast, salads, or sandwiches for healthy fats and fiber. 🥑",
        "Garnish meals with fresh herbs like parsley or cilantro for added flavor and nutrients. 🌿",
        "Have a 'veggie-first' approach: start your meal with a salad or a plate of steamed vegetables. 🥦"
    ]
}

# --- GLOBAL PLACEHOLDER TEXT ---
AI_PLACEHOLDER_TEXT = "Content currently unavailable. Please try regenerating or consult your plan."

# --- Session State Initialization ---
def initialize_session_state():
    if "api_key" not in st.session_state:
        st.session_state.api_key = None
    if "holistic_user_data" not in st.session_state:
        st.session_state.holistic_user_data = {}
    if "wellness_plan" not in st.session_state:
        st.session_state.wellness_plan = None
    if "raw_plan_json" not in st.session_state: # Store raw JSON for better fallback
        st.session_state.raw_plan_json = None
    if "progress" not in st.session_state:
        st.session_state.progress = {}
    if "habit_values" not in st.session_state:
        st.session_state.habit_values = {}
    if "show_content" not in st.session_state:
        st.session_state.show_content = False
    if "qa_response" not in st.session_state:
        st.session_state.qa_response = None
    if "success_message_trigger" not in st.session_state:
        st.session_state.success_message_trigger = False
    if "last_rerun_time" not in st.session_state:
        st.session_state.last_rerun_time = time.time()
    if "tip_idx" not in st.session_state:
        st.session_state.tip_idx = 0
    if "tip_category" not in st.session_state:
        st.session_state.tip_category = "Reduce Stress"
    if "last_tip_switch_time" not in st.session_state:
        st.session_state.last_tip_switch_time = time.time()
    if "all_fallback_content_generated" not in st.session_state: # Flag to track if we're in full fallback mode
        st.session_state.all_fallback_content_generated = False
    if "used_default_tip_indices" not in st.session_state: # To avoid repeating default tips within a generated plan
        st.session_state.used_default_tip_indices = {"stress": set(), "habit": set()}
    if "generated_tasks_per_day" not in st.session_state: # Track generated tasks to avoid repetition
        st.session_state.generated_tasks_per_day = {}

initialize_session_state()

# Streamlit configuration
st.set_page_config(page_title="Holistic Wellness Planner", page_icon="🧠", layout="wide")

# Custom CSS for Tailwind-inspired styling
st.markdown("""
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .stButton>button {
        background-color: #3b82f6; color: white; padding: 0.5rem 1rem;
        border-radius: 0.375rem; border: none; font-weight: 600;
        transition: transform 0.2s ease-in-out, background-color 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05); background-color: #2563eb;
    }
    .next-tip-button {
        background-color: #ffffff; color: #3b82f6; padding: 0.5rem 1rem;
        border: 1px solid #3b82f6; border-radius: 0.375rem; font-weight: 600;
        transition: transform 0.2s ease-in-out, background-color 0.2s;
    }
    .next-tip-button:hover {
        transform: scale(1.05); background-color: #eff6ff;
    }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select {
        border: 1px solid #d1d5db; border-radius: 0.375rem; padding: 0.5rem;
        transition: transform 0.2s ease-in-out;
    }
    .stTextInput>div>input:focus, .stNumberInput>div>input:focus, .stSelectbox>div>select:focus {
        transform: scale(1.02);
    }
    .result-box {
        background: linear-gradient(to right, #ffffff, #f8fafc);
        border: 1px solid #e5e7eb; border-radius: 0.5rem;
        padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.3s ease-in-out;
    }
    .task-card {
        background: linear-gradient(to right, #f8fafc, #e6f0ff);
        border: 1px solid #d1d5db; border-radius: 0.5rem;
        padding: 1rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.3s ease-in-out, box-shadow 0.3s;
    }
    .task-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .progress-bar {
        background-color: #e5e7eb; border-radius: 0.25rem; height: 0.5rem;
        overflow: hidden;
    }
    .progress-fill {
        background: linear-gradient(to right, #3b82f6, #10b981);
        height: 100%; transition: width 0.3s ease-in;
    }
    .emoji-pulse {
        display: inline-block; animation: pulse 1.5s infinite; margin-left: 0.5rem;
    }
    .result-text {
        font-size: 1.25rem; font-weight: 600; color: #1f2937;
    }
    .tip-box {
        background-color: #e0f2fe;
        border: 1px solid #3b82f6;
        border-radius: 0.375rem;
        padding: 1rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #1e40af;
    }
    .plan-expander {
        background: linear-gradient(to right, #f0f9ff, #e0f2fe);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
        line-height: 1.6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .stress-task-container {
        background: linear-gradient(to right, #e0f2fe, #dbeafe);
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
    }
    .habit-task-container {
        background: linear-gradient(to right, #ecfdf5, #d1fae5);
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #10b981;
    }
    .task-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    .habit-task-container .task-title {
        color: #065f46;
    }
    .task-detail {
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }
    .task-tip {
        font-style: italic;
        font-size: 0.9rem;
        color: #6b7280;
        margin-top: 0.8rem;
        border-top: 1px dashed #d1dbdb;
        padding-top: 0.5rem;
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
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .stSidebar .stButton>button {
        background-color: #ffffff;
        color: #3b82f6;
        border: 1px solid #3b82f6;
        border-radius: 0.375rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: transform 0.2s ease-in-out, background-color 0.2s;
    }
    .stSidebar .stButton>button:hover {
        background-color: #eff6ff;
        transform: scale(1.05);
    }
    .qa-response-content {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #333;
    }
    .qa-response-content strong {
        color: #1e40af; /* Dark blue for emphasis */
    }
    .qa-response-content em {
        color: #6b7280; /* Grey for italics */
    }
</style>
""", unsafe_allow_html=True)

# Emoji sets for random selection
EMOJI_SETS = {
    "stress": ["🧘🏻‍♀️", "🥳", "🍀","💐","🌿", "🕉️", "😊", "🌳", "🕊️", "😌", "💖"],
    "habit_veggies": ["🥗","🍏","🥑","🚶🏻‍♀️", "🥕", "🥦", "🍅", "🌽", "🥒", "🥬", "🌱", "💚"],
    "habit_water": ["💧", "🥤", "🚰", "🍋", "🧊","","🥗"],
    "habit_sleep": ["💤", "🛌", "🌙", "⭐","😴","🌓","🎑"],
    "habit_mindfulness": ["🧠", "🌼", "🕊️", "🧘🏻", "🌬️","🏃🏻‍♀️"]
}

# Helper function to clean and format text, ensuring proper punctuation, spacing, and English.
def clean_and_format_text(text):
    if not isinstance(text, str):
        return ""

    # 1. Handle potential encoding issues
    try:
        text = text.encode('utf-8', 'ignore').decode('utf-8')
    except Exception as e:
        logging.warning(f"Encoding/decoding issue in clean_and_format_text: {e}")

    # 2. Remove emojis and unwanted characters
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F800-\U0001F8FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027BF"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed CJK Letters and Months
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "]+", flags=re.UNICODE
    )
    cleaned_text = emoji_pattern.sub('', text)

    # Remove non-alphanumeric characters except common punctuation, then clean whitespace
    # This is more specific to remove unwanted symbols while keeping periods, commas, etc.
    cleaned_text = re.sub(r'[^\w\s\'".,!?;:-]', '', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip() # Normalize whitespace

    # 3. Correct common English phrasing issues
    # Replace "510 minutes" with "5–10 minutes"
    cleaned_text = re.sub(r'(\d+)10 minutes', r'\1–10 minutes', cleaned_text)
    cleaned_text = re.sub(r'510 minutes', '5–10 minutes', cleaned_text) # Specific case

    # Insert space after periods followed by an uppercase letter (for sentences)
    cleaned_text = re.sub(r'\.(?=[A-Z])', '. ', cleaned_text)
    # Insert space after period if it's followed by a letter (handles cases like 'breaks.Research')
    cleaned_text = re.sub(r'\.(?=[a-zA-Z])', '. ', cleaned_text)
    # Remove space before punctuation
    cleaned_text = re.sub(r'\s+([.,!?;:])', r'\1', cleaned_text)
    # Ensure periods at the end of sentences if not already present
    sentences = re.split(r'(?<=[.!?])\s*', cleaned_text)
    formatted_sentences = []
    for s in sentences:
        s = s.strip()
        if s and not s.endswith(('.', '!', '?')):
            formatted_sentences.append(s + '.')
        elif s:
            formatted_sentences.append(s)
    cleaned_text = " ".join(formatted_sentences)

    # Replace 'e.g.' with '(e.g., ...)' or 'for example'
    cleaned_text = re.sub(r'e\.g\.', r'(e.g.,', cleaned_text) # Assuming it will be followed by content, will add closing ) if needed
    cleaned_text = re.sub(r'for example', r'for example', cleaned_text) # Standardize

    # 4. Ensure English output - this is a general check
    english_letters = re.findall(r'[a-zA-Z]', cleaned_text)
    non_ascii_chars = re.findall(r'[^\x00-\x7F]', cleaned_text)

    if cleaned_text and (len(non_ascii_chars) > len(english_letters) * 2 or (len(cleaned_text) < 50 and len(non_ascii_chars) > 5)):
        logging.warning(f"Detected potential non-English content after cleaning: '{cleaned_text[:50]}...'.")

    if not re.search(r'[a-zA-Z0-9]', cleaned_text):
        return ""

    # Final cleanup for extra spaces around punctuation
    cleaned_text = re.sub(r'\s+([.,!?;:])', r'\1', cleaned_text)
    cleaned_text = re.sub(r'([.,!?;:])\s+', r'\1 ', cleaned_text)
    cleaned_text = cleaned_text.strip()

    # Ensure that if "(e.g.," was inserted, it gets a closing ")" if needed
    if "(e.g.," in cleaned_text and not cleaned_text.endswith(")"):
        # Find the last sentence or segment ending before a potential closing parenthesis
        # This is tricky, will assume for now it's part of the current sentence it's in.
        # A more robust solution would involve proper sentence parsing.
        pass # For now, let's keep it simple and rely on the AI to finish the thought.

    return cleaned_text

# Sidebar: Quick Wellness Tips
with st.sidebar:
    st.header("💡 Quick Wellness Tips")
    st.caption("Here are some personalized tips tailored to your 🎯selected Goal. ✨")

    current_tip_category = st.session_state.holistic_user_data.get("Goal", "Reduce Stress")
    st.session_state.tip_category = current_tip_category # Update session state

    current_tips_list = TIPS.get(st.session_state.tip_category, TIPS["Reduce Stress"])
    tip_slot = st.empty()

    if current_tips_list:
        # Ensure tip_idx is within bounds for the current list
        st.session_state.tip_idx = st.session_state.tip_idx % len(current_tips_list)
        tip_slot.info(current_tips_list[st.session_state.tip_idx])
    else:
        tip_slot.info("No tips available for this category.")

    if st.button("Next Tip", key="next_tip_manual"):
        if current_tips_list:
            st.session_state.tip_idx = (st.session_state.tip_idx + 1) % len(current_tips_list)
            st.session_state.last_tip_switch_time = time.time()
            tip_slot.info(current_tips_list[st.session_state.tip_idx])
        else:
            tip_slot.info("No tips available for this category.")

    tip_switch_interval = 6
    if current_tips_list and (time.time() - st.session_state.last_tip_switch_time > tip_switch_interval):
        st.session_state.tip_idx = (st.session_state.tip_idx + 1) % len(current_tips_list)
        st.session_state.last_tip_switch_time = time.time()
        tip_slot.info(current_tips_list[st.session_state.tip_idx])

# Check for API Key
if not st.session_state.api_key:
    st.markdown(
        """
        <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
            🧠 Holistic Wellness Planner
        </h1>
        <p style='text-align:center; font-size:1.1rem; color:#6c757d;'>
            Create a personalized plan to manage stress and build healthy habits! 🧘‍♀️✨ <span class='emoji-pulse'>✨</span>
        </p>
        """,
        unsafe_allow_html=True
    )
    st.warning("⚠️ Please enter a valid API key in the FitForge_Hub🚀 page sidebar")
    st.stop()

# Initialize OpenAI client
def initialize_client(api_key):
    try:
        client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        st.error(f"🚨 Failed to initialize OpenAI client: {e}")
        return None

client = initialize_client(st.session_state["api_key"])
if not client:
    st.stop()

# Helper functions
def safe_int(value, default=0):
    try: return int(value)
    except (TypeError, ValueError): return default

def safe_float(value, default=0.0):
    try: return float(value)
    except (TypeError, ValueError): return default

def clean_and_translate_to_english(text):
    """
    Cleans text by removing emojis, unwanted characters, and extra whitespace,
    and ensures the output is in English. If the input is already English,
    it cleans it. If it's in another language, it attempts to keep it in English.
    Returns an empty string if the cleaned text is effectively empty.
    Also applies basic formatting corrections.
    """
    cleaned = clean_and_format_text(text) # Use the new more comprehensive cleaning function
    return cleaned


def get_random_emoji(task_type, goal):
    if task_type == "stress":
        return random.choice(EMOJI_SETS.get("stress", ["😌"]))
    elif task_type == "habit":
        if goal == "Eat More Vegetables":
            return random.choice(EMOJI_SETS.get("habit_veggies", ["🌱"]))
        elif goal == "Increase Water Intake":
            return random.choice(EMOJI_SETS.get("habit_water", ["💧"]))
        elif goal == "Improve Sleep":
            return random.choice(EMOJI_SETS.get("habit_sleep", ["💤"]))
        elif goal == "Increase Mindfulness":
            return random.choice(EMOJI_SETS.get("habit_mindfulness", ["🧘"]))
        else:
            return "✨"
    return "✨"

def get_default_tip_for_goal(goal, task_type, excluded_indices=None):
    if excluded_indices is None:
        excluded_indices = set()

    tips_for_category = TIPS.get(goal, TIPS["Reduce Stress"])
    available_indices = [i for i, tip in enumerate(tips_for_category) if i not in excluded_indices]

    if not available_indices:
        logging.warning(f"All tips for goal '{goal}' have been used. Resetting and picking again.")
        available_indices = list(range(len(tips_for_category)))

    if not available_indices:
        return f"No specific default tip found for your goal: {goal}.", -1

    chosen_index = random.choice(available_indices)
    return tips_for_category[chosen_index], chosen_index

def get_personalized_default_content(task_type, goal, user_data, is_full_fallback=False):
    prefix = "[DEFAULT] " if is_full_fallback else ""
    if task_type == "stress_task":
        base_title_part = "Stress Management Task"
    elif task_type == "habit_task":
        base_title_part = f"{goal} Habit Task"
    else:
        base_title_part = "Wellness Task"

    default_title = f"{prefix}{base_title_part}" if is_full_fallback else base_title_part
    default_description = ""
    default_benefit = ""
    default_tip = ""
    emoji = get_random_emoji(task_type, goal)
    min_content_chars = 80

    if task_type == "stress_task":
        tip_text, tip_idx_used = get_default_tip_for_goal("Reduce Stress", "stress", st.session_state.used_default_tip_indices["stress"])
        default_description = tip_text
        if tip_idx_used != -1:
            st.session_state.used_default_tip_indices["stress"].add(tip_idx_used)
    elif task_type == "habit_task":
        tip_text, tip_idx_used = get_default_tip_for_goal(goal, "habit", st.session_state.used_default_tip_indices["habit"])
        default_description = tip_text
        if tip_idx_used != -1:
            st.session_state.used_default_tip_indices["habit"].add(tip_idx_used)

    if not default_description.strip() or (default_description != AI_PLACEHOLDER_TEXT and len(default_description) < min_content_chars):
        if task_type == "stress_task":
            default_description = "Dedicate focused time to this creative or restorative activity to help calm your mind and release daily tension. Engage fully in the process for maximum benefit." if len(default_description) < min_content_chars else default_description
        else: # habit_task
            default_description = f"Consistently perform this action to build a strong habit towards your goal of {goal}. Small, regular efforts lead to significant long-term progress." if len(default_description) < min_content_chars else default_description
        if len(default_description) < min_content_chars:
             default_description = AI_PLACEHOLDER_TEXT

    if task_type == "stress_task":
        default_benefit = "Engaging in this stress management activity enhances your ability to cope with daily challenges, promoting emotional resilience and a sense of calm. It supports mental clarity and reduces the physiological effects of stress."
    elif task_type == "habit_task":
        if goal == "Increase Water Intake":
            default_benefit = "Staying hydrated is crucial for maintaining energy levels, supporting cognitive function, regulating body temperature, and aiding digestion. This habit contributes to overall physical health and well-being. Proper hydration also aids in stress reduction and overall wellness."
        elif goal == "Eat More Vegetables":
            default_benefit = "A diet rich in vegetables provides essential vitamins, minerals, fiber, and antioxidants that bolster immunity, improve digestion, and protect against chronic diseases, contributing to long-term health and vitality."
        elif goal == "Improve Sleep":
            default_benefit = "Prioritizing sleep is fundamental for physical recovery, cognitive performance, memory consolidation, and emotional regulation. Consistent, quality sleep is key to overall health and daily functioning."
        elif goal == "Increase Mindfulness":
            default_benefit = "Practicing mindfulness cultivates present-moment awareness, which can reduce stress, enhance focus, improve emotional regulation, and foster a greater appreciation for life's experiences. It trains your mind to be more present."
        else:
            default_benefit = f"Regularly engaging in this habit will contribute significantly to your overall well-being and help you achieve your goal of {goal}. Consistency is key for lasting positive change."

    if len(default_benefit) < min_content_chars:
        default_benefit = AI_PLACEHOLDER_TEXT

    if task_type == "stress_task":
        default_tip = "Integrate this activity into your daily or weekly routine. Even short, consistent practice can yield significant benefits for stress reduction and mental well-being. Find a time when you can be uninterrupted."
    elif task_type == "habit_task":
        if goal == "Increase Water Intake":
            default_tip = "To drink more water daily: Set reminders (phone alerts/apps). Drink a glass upon waking. Flavor with lemon/cucumber/mint. Track intake via a marked bottle or app. Pairing hydration with existing habits like mindfulness can increase adherence. Staying hydrated supports stress reduction and overall wellness."
        elif goal == "Eat More Vegetables":
            default_tip = "Explore different cooking methods and seasonings to keep vegetable consumption exciting. Having pre-prepped vegetables readily available can also significantly increase intake throughout the day. Aim for a variety of colors to ensure a broad spectrum of nutrients."
        elif goal == "Improve Sleep":
            default_tip = "Create a consistent wind-down routine in the hour before bed. This signals to your body that it's time to prepare for sleep, aiding in falling asleep faster and improving sleep quality. Avoid screens before bed as blue light can disrupt melatonin production."
        elif goal == "Increase Mindfulness":
            default_tip = "Start small by practicing for just a few minutes each day. Focus on a single anchor, like your breath, and gently guide your attention back whenever your mind wanders. Consistency is more important than duration."
        else:
            default_tip = f"To successfully build the habit of {goal.lower()}, start with an achievable commitment and gradually increase the challenge. Track your progress and celebrate small wins to stay motivated."

    if len(default_tip) < min_content_chars:
        default_tip = AI_PLACEHOLDER_TEXT

    return {
        "title": default_title,
        "description": default_description,
        "benefit": default_benefit,
        "pro_tips": default_tip,
        "emoji": emoji
    }

def validate_plan(plan_data, days):
    validation_errors = []
    min_content_chars = 80

    for day_idx in range(1, days + 1):
        day_key = f"day_{day_idx}"
        if day_key not in plan_data:
            validation_errors.append(f"Missing day key: '{day_key}'")
            continue
        day_tasks = plan_data[day_key]
        if not isinstance(day_tasks, dict):
            validation_errors.append(f"Invalid format for {day_key}: expected a dictionary, got {type(day_tasks)}")
            continue

        for task_type in ["stress_task", "habit_task"]:
            if task_type not in day_tasks:
                validation_errors.append(f"Missing task type '{task_type}' in {day_key}")
                continue
            task_content = day_tasks[task_type]
            if not isinstance(task_content, dict):
                validation_errors.append(f"Invalid format for {day_key}.{task_type}: expected a dictionary, got {type(task_content)}")
                continue

            for field in ['title', 'description', 'benefit', 'pro_tips']:
                val = task_content.get(field, '').strip()

                if field == 'title':
                    if not val:
                        validation_errors.append(f"{day_key}.{task_type}.{field} is empty.")
                    elif not (1 <= len(val.split()) <= 15):
                        validation_errors.append(f"{day_key}.{task_type}.{field} has incorrect word count ({len(val.split())}). Value: '{val}'")
                elif field in ['description', 'benefit', 'pro_tips']:
                    if val != AI_PLACEHOLDER_TEXT and len(val) < min_content_chars:
                        validation_errors.append(f"{day_key}.{task_type}.{field} is too short (less than {min_content_chars} chars). Raw value length: {len(val)}. Raw value: '{val}'")
                    cleaned_val = clean_and_translate_to_english(val)
                    if val != AI_PLACEHOLDER_TEXT and not cleaned_val:
                        validation_errors.append(f"{day_key}.{task_type}.{field} cleaned to nothing, and was not the explicit placeholder '{AI_PLACEHOLDER_TEXT}'. Original: '{val}'")
    if validation_errors:
        logging.warning(f"Validation errors: {'; '.join(validation_errors)}")
        raise ValueError(f"JSON validation failed: {'; '.join(validation_errors)}")
    logging.info("Plan data passed hard validation.")

def generate_wellness_plan(local_data):
    try:
        days_str = local_data["Plan_Duration"]
        match = re.search(r'(\d+)\s+Days?', days_str)
        days = int(match.group(1)) if match else 7
    except Exception as e:
        logging.error(f"Error parsing Plan_Duration '{local_data.get('Plan_Duration', 'N/A')}': {e}")
        days = 7

    logging.info(f"Attempting to generate a {days}-day wellness plan.")

    st.session_state.used_default_tip_indices = {"stress": set(), "habit": set()}
    st.session_state.generated_tasks_per_day = {f"day_{d+1}": {"stress": None, "habit": None} for d in range(days)}
    st.session_state.all_fallback_content_generated = False

    workload_intensity_map = {"Low": 1, "Moderate": 2, "High": 3}
    social_support_map = {"Low": 1, "Moderate": 2, "High": 3}
    stress_level_map = {"Low": 1, "Moderate": 2, "High": 3}

    # Ensure AI generates scientifically sound advice.
    # Example of a refined prompt for a specific scenario:
    # "To reduce workload stress with your current profile, start by integrating short, regular mindfulness sessions (5–10 minutes) into your work breaks. Research shows this lowers cortisol and improves focus. ✅ Prioritize task batching and time-blocking to create clear boundaries between work and relaxation. ✨ Since you already get 7 hours of sleep and 1 hour of daily relaxation, enhance that downtime with screen-free activities like reading or gentle stretching to promote mental recovery. 💡 Lastly, leverage your moderate social support by scheduling brief check-ins with colleagues or friends to foster connection and emotional resilience. 😌 These small, science-backed steps can significantly ease stress without overhauling your routine. 🌳"

    prompt = f"""
You are a senior wellness copywriter and a behavioral science expert.
Output a {days}-day wellness plan in **strict JSON**.
Each day **must** contain:
- stress_task
- habit_task
Each task **must** include:
- title (must be between 1 and 15 words)
- description (≥80 characters, or "{AI_PLACEHOLDER_TEXT}")
- benefit (≥80 characters, or "{AI_PLACEHOLDER_TEXT}")
- pro_tips (≥80 characters, or "{AI_PLACEHOLDER_TEXT}")

**User Profile Context**:
- Workload Intensity: {local_data["Workload_Intensity"]} (mapped to {workload_intensity_map.get(local_data["Workload_Intensity"], 'N/A')})
- Social Support Level: {local_data["Social_Support"]} (mapped to {social_support_map.get(local_data["Social_Support"], 'N/A')})
- Relaxation Time (hours/day): {local_data["Relaxation_Time"]:.1f}
- Mindfulness Practice Frequency (per week): {local_data["Mindfulness_Frequency"]}
- Sleep Hours: {local_data["Sleep_Hours"]:.1f}
- Stress Level: {local_data["Stress_Level"]} (mapped to {stress_level_map.get(local_data["Stress_Level"], 'N/A')})
- Goal: {local_data["Goal"]}

**Hard Rules**:
1. Any field < 80 characters that is NOT "{AI_PLACEHOLDER_TEXT}" is considered **a failure** and will immediately trigger a retry.
2. Title MUST be between 1 and 15 words. If it's not, it's a failure.
3. Do not return empty strings, null values, or pure emojis for any field.
4. Prohibit repetitive phrasing within and across tasks and days. Specifically, ensure the titles and core concepts of tasks are distinct for each day.
5. **ALL output MUST be in clear, grammatically correct ENGLISH. Do NOT include any Chinese characters or mixed-language phrases. If you accidentally generate text in another language, translate it to English AND clean it.**
6. If you cannot generate specific, high-quality content for description, benefit, or pro_tips, use "{AI_PLACEHOLDER_TEXT}" for that field. However, try to be as specific as possible using the provided user profile context.
7. Ensure that tasks generated for different days are distinct. If a task is very similar to one from a previous day, create a variation or a completely new task.
8. The `title` should be a concise summary of the task. The `description` should be more detailed.
9.  **Prioritize scientific grounding**: base recommendations on established research in psychology, behavioral science, and public health. When mentioning statistics or research findings, do so accurately and concisely.
10. **Use correct English grammar and punctuation**: This includes using em dashes (–) for ranges (e.g., 5–10 minutes), ensuring correct spacing around punctuation (e.g., "work breaks. Research"), and employing clear sentence structures. Replace informal abbreviations like "e.g." with "(e.g., ...)" or "for example" where appropriate for flow.

Required structure:
{{
  "day_1":{{
    "stress_task":{{
      "title":"...title between 1 and 15 words...",
      "description":"...≥80 chars or {AI_PLACEHOLDER_TEXT}...",
      "benefit":"...≥80 chars or {AI_PLACEHOLDER_TEXT}...",
      "pro_tips":"...≥80 chars or {AI_PLACEHOLDER_TEXT}..."
    }},
    "habit_task":{{
      "title":"...title between 1 and 15 words...",
      "description":"...≥80 chars or {AI_PLACEHOLDER_TEXT}...",
      "benefit":"...≥80 chars or {AI_PLACEHOLDER_TEXT}...",
      "pro_tips":"...≥80 chars or {AI_PLACEHOLDER_TEXT}..."
    }}
  }},
  ... // up to day_{days}
}}
"""

    max_retries = 10
    initial_temperature = 0.7

    for attempt in range(max_retries):
        current_temperature = initial_temperature + attempt * 0.15
        logging.info(f"Attempt {attempt + 1}/{max_retries} to generate wellness plan. Temperature: {current_temperature:.2f}")
        start_time = time.time()

        try:
            logging.info("Sending prompt to OpenAI API.")
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=current_temperature
            )
            raw_json_string = response.choices[0].message.content.strip()
            response_time = time.time() - start_time
            logging.info(f"Received raw AI response in {response_time:.2f} seconds.")
            logging.debug(f"Raw AI Response (Attempt {attempt+1}, Temp: {current_temperature:.2f}):\n{raw_json_string}")

            start_brace = raw_json_string.find('{')
            end_brace = raw_json_string.rfind('}')

            if start_brace == -1 or end_brace == -1 or start_brace >= end_brace:
                raise ValueError("Could not find a valid JSON object in the response. Raw response: " + raw_json_string)

            json_content = raw_json_string[start_brace:end_brace+1]
            logging.info("Attempting to parse JSON response.")
            plan_data = json.loads(json_content)
            logging.info("JSON parsed successfully.")

            generated_stress_titles = set()
            generated_habit_titles = set()

            for i in range(1, days + 1):
                day_key = f"day_{i}"
                if day_key not in plan_data:
                    raise ValueError(f"Missing day key: '{day_key}' in parsed JSON.")
                day_tasks = plan_data[day_key]
                if not isinstance(day_tasks, dict):
                    raise ValueError(f"Invalid format for {day_key}: expected a dictionary, got {type(day_tasks)}.")

                stress_task_data = day_tasks.get("stress_task", {})
                stress_title = clean_and_translate_to_english(stress_task_data.get("title", "")).lower()
                if stress_title:
                    if stress_title in generated_stress_titles:
                        raise ValueError(f"Repetitive stress task title found on Day {i}: '{stress_task_data.get('title', '')}'. Titles must be unique across the entire plan.")
                    generated_stress_titles.add(stress_title)
                    st.session_state.generated_tasks_per_day[f"day_{i}"]["stress"] = stress_task_data
                else:
                    logging.warning(f"Missing or empty stress task title on Day {i}.")
                    raise ValueError(f"Missing or empty stress task title on Day {i}.")

                habit_task_data = day_tasks.get("habit_task", {})
                habit_title = clean_and_translate_to_english(habit_task_data.get("title", "")).lower()
                if habit_title:
                    if habit_title in generated_habit_titles:
                        raise ValueError(f"Repetitive habit task title found on Day {i}: '{habit_task_data.get('title', '')}'. Titles must be unique across the entire plan.")
                    generated_habit_titles.add(habit_title)
                    st.session_state.generated_tasks_per_day[f"day_{i}"]["habit"] = habit_task_data
                else:
                    logging.warning(f"Missing or empty habit task title on Day {i}.")
                    raise ValueError(f"Missing or empty habit task title on Day {i}.")

            validate_plan(plan_data, days)

            logging.info("Validation passed. Formatting plan.")
            st.session_state.raw_plan_json = plan_data

            st.session_state.progress = {}
            st.session_state.habit_values = {}
            for i in range(days):
                day_key = f"Day {i+1}"
                st.session_state.progress[day_key] = {"Stress": False, "Habit": False}
                st.session_state.habit_values[day_key] = 0.0
            logging.info("Initialized session state for progress and habit values.")

            formatted_plan_days = []
            for i in range(days):
                day_key_in_json = f"day_{i+1}"
                day_content = plan_data.get(day_key_in_json, {})

                stress_task_raw = day_content.get("stress_task", {})
                habit_task_raw = day_content.get("habit_task", {})

                is_stress_ai_valid = False
                if (stress_task_raw.get("title", "").strip() and 1 <= len(stress_task_raw.get("title", "").split()) <= 15) and \
                   (stress_task_raw.get("description", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(stress_task_raw.get("description", "")) >= 80) and \
                   (stress_task_raw.get("benefit", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(stress_task_raw.get("benefit", "")) >= 80) and \
                   (stress_task_raw.get("pro_tips", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(stress_task_raw.get("pro_tips", "")) >= 80):
                    is_stress_ai_valid = True

                is_habit_ai_valid = False
                if (habit_task_raw.get("title", "").strip() and 1 <= len(habit_task_raw.get("title", "").split()) <= 15) and \
                   (habit_task_raw.get("description", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(habit_task_raw.get("description", "")) >= 80) and \
                   (habit_task_raw.get("benefit", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(habit_task_raw.get("benefit", "")) >= 80) and \
                   (habit_task_raw.get("pro_tips", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(habit_task_raw.get("pro_tips", "")) >= 80):
                    is_habit_ai_valid = True

                stress_task_html = ""
                if is_stress_ai_valid:
                    display_stress_title = clean_and_translate_to_english(stress_task_raw.get('title', 'Stress Management Task'))
                    if not stress_task_raw.get('title', '').startswith("[DEFAULT]"):
                        display_stress_title = f"✨ {display_stress_title}"

                    stress_task_html = f"""
                    <div class='stress-task-container'>
                        <h4><strong>{display_stress_title}</strong> {get_random_emoji("stress", local_data["Goal"])}</h4>
                        {format_task_section(
                            stress_task_raw.get("title", "Stress Management Task"),
                            stress_task_raw.get("description", AI_PLACEHOLDER_TEXT),
                            stress_task_raw.get("benefit", AI_PLACEHOLDER_TEXT),
                            stress_task_raw.get("pro_tips", AI_PLACEHOLDER_TEXT),
                            get_random_emoji("stress", local_data["Goal"]),
                            is_ai_generated_valid=True
                        )}
                    </div>
                    """
                else:
                    stress_default_content = get_personalized_default_content("stress_task", local_data["Goal"], local_data, is_full_fallback=True)
                    stress_task_html = f"""
                    <div class='stress-task-container'>
                        <h4><strong>{stress_default_content['title']}</strong> {stress_default_content['emoji']}</h4>
                        {format_task_section(
                            stress_default_content['title'],
                            stress_default_content['description'],
                            stress_default_content['benefit'],
                            stress_default_content['pro_tips'],
                            stress_default_content['emoji'],
                            is_ai_generated_valid=False
                        )}
                    </div>
                    """

                habit_task_html = ""
                if is_habit_ai_valid:
                    display_habit_title = clean_and_translate_to_english(habit_task_raw.get('title', 'Habit Building Task'))
                    if not habit_task_raw.get('title', '').startswith("[DEFAULT]"):
                        display_habit_title = f"✨ {display_habit_title}"

                    habit_task_html = f"""
                    <div class='habit-task-container'>
                        <h4><strong>{display_habit_title}</strong> {get_random_emoji("habit", local_data["Goal"])}</h4>
                        {format_task_section(
                            habit_task_raw.get("title","Habit Building Task"),
                            habit_task_raw.get("description", AI_PLACEHOLDER_TEXT),
                            habit_task_raw.get("benefit", AI_PLACEHOLDER_TEXT),
                            habit_task_raw.get("pro_tips", AI_PLACEHOLDER_TEXT),
                            get_random_emoji("habit", local_data["Goal"]),
                            is_ai_generated_valid=True
                        )}
                    </div>
                    """
                else:
                    habit_default_content = get_personalized_default_content("habit_task", local_data["Goal"], local_data, is_full_fallback=True)
                    habit_task_html = f"""
                    <div class='habit-task-container'>
                        <h4><strong>{habit_default_content['title']}</strong> {habit_default_content['emoji']}</h4>
                        {format_task_section(
                            habit_default_content['title'],
                            habit_default_content['description'],
                            habit_default_content['benefit'],
                            habit_default_content['pro_tips'],
                            habit_default_content['emoji'],
                            is_ai_generated_valid=False
                        )}
                    </div>
                    """

                formatted_plan_days.append(f"### Day {i+1}\n{stress_task_html}\n{habit_task_html}")

            logging.info(f"Successfully generated and validated wellness plan for {days} days in {time.time() - start_time:.2f} seconds on attempt {attempt+1}.")
            return '\n\n'.join(formatted_plan_days), days

        except (json.JSONDecodeError, ValueError, RuntimeError) as e:
            logging.warning(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1.5)
                logging.info(f"Retrying generation. Next attempt with temperature up to {initial_temperature + (attempt + 1) * 0.15:.2f}")
            else:
                logging.error("Max retries reached. Falling back to purely TIPS-based plan generation.")
                st.session_state.all_fallback_content_generated = True

                formatted_plan_days = []
                for i in range(days):
                    stress_default = get_personalized_default_content("stress_task", local_data["Goal"], local_data, is_full_fallback=True)
                    habit_default = get_personalized_default_content("habit_task", local_data["Goal"], local_data, is_full_fallback=True)

                    stress_task_html = f"""
                    <div class='stress-task-container'>
                        <h4><strong>{stress_default['title']}</strong> {stress_default['emoji']}</h4>
                        {format_task_section(stress_default['title'], stress_default['description'], stress_default['benefit'], stress_default['pro_tips'], stress_default['emoji'], is_ai_generated_valid=False)}
                    </div>
                    """
                    habit_task_html = f"""
                    <div class='habit-task-container'>
                        <h4><strong>{habit_default['title']}</strong> {habit_default['emoji']}</h4>
                        {format_task_section(habit_default['title'], habit_default['description'], habit_default['benefit'], habit_default['pro_tips'], habit_default['emoji'], is_ai_generated_valid=False)}
                    </div>
                    """
                    formatted_plan_days.append(f"### Day {i+1}\n{stress_task_html}\n{habit_task_html}")
                logging.info(f"Generated default plan for {days} days using personalized fallbacks.")
                st.session_state.progress = {}
                st.session_state.habit_values = {}
                for i in range(days):
                    day_key = f"Day {i+1}"
                    st.session_state.progress[day_key] = {"Stress": False, "Habit": False}
                    st.session_state.habit_values[day_key] = 0.0
                return '\n\n'.join(formatted_plan_days), days

        except Exception as e:
            logging.error(f"An unexpected error occurred on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1.5)
            else:
                raise RuntimeError(f"An unexpected error occurred after {max_retries} retries. Last error: {e}")
    raise RuntimeError("Wellness plan generation loop completed without returning a plan or raising an error.")

# Main content
st.markdown(
    """
    <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
        🧠 Holistic Wellness Planner
    </h1>
    <p style='text-align:center; font-size:1.1rem; color:#6c757d;'>
        Create a personalized plan to manage stress and build healthy habits! 🧘‍♀️✨ <span class='emoji-pulse'>✨</span>
    </p>
    """,
    unsafe_allow_html=True
)

# Interactive Q&A
st.markdown("<h3><span class='emoji-pulse'>💬</span> Ask About Your Wellness Plan</h3>", unsafe_allow_html=True)
custom_query = st.text_input("💬 Describe your custom query:", placeholder="e.g., How can I improve my sleep quality? 🤔", key="custom_query_input")
example_queries = [
    "Select an example query...",
    "How can I reduce my workload stress? 😌",
    "What are some tips to improve my sleep quality? 💤",
    "How can I stick to drinking more water daily? 💧",
    "How does mindfulness practice affect my stress? 🧘‍♀️",
    "What are some quick stress-relief techniques I can use at work? ⏱️"
]
query = st.selectbox("💡 Choose an example or type your own:", example_queries, index=0, key="example_query_select")

if st.button("Submit Question 🗣️", key="submit_query_btn"):
    question = custom_query.strip() or (query if query != "Select an example query..." else "")
    if not question:
        st.error("🚨 Please enter a question or select an example query.")
    else:
        logging.info(f"Submitting Q&A query: {question}")
        local_data = st.session_state.holistic_user_data
        qna_placeholder_fallback_message = "Content unavailable. For more specific guidance, please ensure your wellness profile is filled out. In the meantime, general principles apply."

        prompt_parts = [
            "You are a professional wellness coach and a behavioral science expert. Provide a concise, evidence-based, and scientifically grounded answer (100-150 words) with actionable tips to the following question:"
        ]

        if local_data:
            prompt_parts.append(f'Consider the user\'s profile for a more tailored response:\n')
            prompt_parts.append(f'- Workload Intensity: **{local_data["Workload_Intensity"]}**')
            prompt_parts.append(f'- Social Support Level: **{local_data["Social_Support"]}**')
            prompt_parts.append(f'- Relaxation Time (hours/day): **{local_data["Relaxation_Time"]:.1f}**')
            prompt_parts.append(f'- Mindfulness Practice Frequency (per week): **{local_data["Mindfulness_Frequency"]}**')
            prompt_parts.append(f'- Sleep Hours: **{local_data["Sleep_Hours"]:.1f}**')
            prompt_parts.append(f'- Stress Level: **{local_data["Stress_Level"]}**')
            prompt_parts.append(f'- Primary Goal: **{local_data["Goal"]}**\n')
        else:
            prompt_parts.append("The user has not provided a detailed wellness profile. Provide general, widely applicable advice.\n")

        prompt_parts.append(f'Question: "**{question}**"\n')
        prompt_parts.append("Include 2–3 relevant emojis to enhance engagement. Ensure the response is practical and grounded in health science. Use correct English grammar and punctuation, including proper spacing and em dashes for ranges if applicable. For example, use '5–10 minutes' not '510 minutes'.")
        prompt_parts.append(f"**CRITICAL INSTRUCTION:** Your entire response MUST be in clear, grammatically correct ENGLISH. Do NOT include any Chinese characters or mixed-language phrases. If the question is in mixed language, answer in English. If you cannot generate a good, personalized response, state \"{qna_placeholder_fallback_message}\"")
        final_prompt = "\n".join(prompt_parts)

        try:
            logging.info("Sending Q&A prompt to OpenAI API.")
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.7
            )
            raw_response_text = response.choices[0].message.content

            # Use the robust cleaning and formatting function
            cleaned_response = clean_and_format_text(raw_response_text)

            if not cleaned_response or qna_placeholder_fallback_message in raw_response_text:
                st.session_state.qa_response = f"<div class='result-box qa-response-content'>{qna_placeholder_fallback_message}</div>"
            else:
                formatted_response = "<div class='result-box qa-response-content'>"
                # Split into segments based on sentence endings followed by spaces or newlines
                response_segments = re.split(r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\n', cleaned_response)

                emoji_cycle = ["✅", "✨", "💡", "😌", "🌳", "🧘‍♀️", "💧", "🍎", "🌟", "🚀", "🧠", "💚", "👍"]
                emoji_index = 0

                for i, segment in enumerate(response_segments):
                    segment = segment.strip()
                    if segment:
                        # Ensure each segment ends with a period if it doesn't already have punctuation
                        if not segment.endswith(('.', '!', '?')):
                            segment += '.'

                        formatted_response += f"<strong>{segment}</strong>"
                        formatted_response += emoji_cycle[emoji_index % len(emoji_cycle)]
                        emoji_index += 1
                        formatted_response += " "
                formatted_response += "</div>"
                st.session_state.qa_response = formatted_response

            logging.info("Q&A response received and processed.")
            st.markdown(st.session_state.qa_response, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"🚨 Failed to get response: {e}")
            logging.error(f"Q&A API call failed: {e}")
            st.session_state.qa_response = f"<div class='result-box qa-response-content'>An error occurred while fetching the response. Please try again.</div>"
            st.markdown(st.session_state.qa_response, unsafe_allow_html=True)

# Main content
st.markdown(
    """
    <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
        🧠 Holistic Wellness Planner
    </h1>
    <p style='text-align:center; font-size:1.1rem; color:#6c757d;'>
        Create a personalized plan to manage stress and build healthy habits! 🧘‍♀️✨ <span class='emoji-pulse'>✨</span>
    </p>
    """,
    unsafe_allow_html=True
)

# User Input Form
st.subheader("📋 Wellness Profile")
with st.form(key="wellness_form"):
    col1, col2 = st.columns(2)

    with col1:
        workload_intensity = st.selectbox("💼 Workload Intensity", ["Low", "Moderate", "High"], index=1, key="local_workload_intensity")
        social_support = st.selectbox("🤝 Social Support Level", ["Low", "Moderate", "High"], index=1, key="local_social_support")
        relaxation_time = st.number_input("🧘‍♀️ Relaxation Time (hours/day)", min_value=0.0, max_value=8.0, value=1.0, step=0.1, key="local_relaxation_time")
        mindfulness_frequency = st.slider("🧠 Mindfulness Practice Frequency (per week)", min_value=0, max_value=7, value=2, step=1, key="local_mindfulness_frequency")
    with col2:
        sleep_hours = st.number_input("😴 Sleep Hours per Night", min_value=4.0, max_value=12.0, value=7.0, step=0.1, key="local_sleep_hours")
        stress_level = st.selectbox("😓 Stress Level", ["Low", "Moderate", "High"], index=1, key="local_stress_level")
        goal = st.selectbox("🎯 Goal", ["Reduce Stress", "Improve Sleep", "Increase Mindfulness", "Increase Water Intake", "Eat More Vegetables"], index=0, key="local_goal")
        plan_duration = st.selectbox("📅 Plan Duration", ["7 Days", "14 Days"], index=0, key="local_plan_duration")
    submitted = st.form_submit_button("Generate Wellness Plan 🚀")

if submitted:
    st.session_state.holistic_user_data = {
        "Workload_Intensity": workload_intensity,
        "Social_Support": social_support,
        "Relaxation_Time": safe_float(relaxation_time, 1.0),
        "Mindfulness_Frequency": safe_int(mindfulness_frequency, 2),
        "Sleep_Hours": safe_float(sleep_hours, 7.0),
        "Stress_Level": stress_level,
        "Goal": goal,
        "Plan_Duration": plan_duration
    }
    logging.info(f"Form submitted with Plan_Duration: {plan_duration}")
    st.session_state.show_content = True
    st.session_state.success_message_trigger = True
    st.session_state.wellness_plan = None
    st.session_state.raw_plan_json = None
    st.session_state.progress = {}
    st.session_state.habit_values = {}
    st.session_state.generated_tasks_per_day = {}
    st.rerun()

if st.session_state.success_message_trigger:
    st.markdown('<div class="success-message">🎉 Profile saved successfully!</div>', unsafe_allow_html=True)
    st.session_state.success_message_trigger = False

# Display Wellness Plan
if st.session_state.show_content and st.session_state.holistic_user_data:
    with st.spinner("Generating your personalized health management plan... 📋"):
        if not st.session_state.wellness_plan:
            try:
                logging.info("Calling generate_wellness_plan function.")
                plan, days = generate_wellness_plan(st.session_state.holistic_user_data)
                st.session_state.wellness_plan = plan
                logging.info(f"Wellness plan generated for {days} days.")

                day_blocks = plan.split('\n\n')
                for day_block in day_blocks:
                    day_match = re.search(r'### Day (\d+)', day_block)
                    if day_match:
                        day_num = int(day_match.group(1))
                        day_key = f"Day {day_num}"
                        if day_key not in st.session_state.progress:
                            st.session_state.progress[day_key] = {"Stress": False, "Habit": False}
                        if day_key not in st.session_state.habit_values:
                            st.session_state.habit_values[day_key] = 0.0
                logging.info("Wellness plan generated and session state updated.")
            except Exception as e:
                st.error(f"Failed to generate plan: {e}")
                logging.error(f"Error during plan generation: {e}")
                st.stop()

        if st.session_state.wellness_plan:
            st.markdown(
                """
                <div class='result-box'>
                    <p class='result-text'>🎉 Your personalized wellness plan is ready! Start your journey now! 💪✨</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            day_blocks = st.session_state.wellness_plan.split('\n\n')

            def get_day_number(block):
                match = re.search(r'### Day (\d+)', block)
                return int(match.group(1)) if match else float('inf')

            sorted_day_blocks = sorted(day_blocks, key=get_day_number)
            raw_plan_json_content = st.session_state.raw_plan_json

            for day_block in sorted_day_blocks:
                day_match = re.search(r'### Day (\d+)', day_block)
                if not day_match:
                    logging.warning(f"Invalid day block format: {day_block}")
                    continue
                day_num = int(day_match.group(1))
                day_title = f"Day {day_num}"

                stress_task_html_rendered = ""
                habit_task_html_rendered = ""

                try:
                    day_json_data = raw_plan_json_content.get(f"day_{day_num}", {}) if raw_plan_json_content else {}

                    raw_stress_task_data = day_json_data.get("stress_task", {})
                    raw_habit_task_data = day_json_data.get("habit_task", {})

                    is_stress_ai_valid = False
                    if (raw_stress_task_data.get("title", "").strip() and 1 <= len(raw_stress_task_data.get("title", "").split()) <= 15) and \
                       (raw_stress_task_data.get("description", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(raw_stress_task_data.get("description", "")) >= 80) and \
                       (raw_stress_task_data.get("benefit", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(raw_stress_task_data.get("benefit", "")) >= 80) and \
                       (raw_stress_task_data.get("pro_tips", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(raw_stress_task_data.get("pro_tips", "")) >= 80):
                        is_stress_ai_valid = True

                    is_habit_ai_valid = False
                    if (raw_habit_task_data.get("title", "").strip() and 1 <= len(raw_habit_task_data.get("title", "").split()) <= 15) and \
                       (raw_habit_task_data.get("description", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(raw_habit_task_data.get("description", "")) >= 80) and \
                       (raw_habit_task_data.get("benefit", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(raw_habit_task_data.get("benefit", "")) >= 80) and \
                       (raw_habit_task_data.get("pro_tips", AI_PLACEHOLDER_TEXT) != AI_PLACEHOLDER_TEXT and len(raw_habit_task_data.get("pro_tips", "")) >= 80):
                        is_habit_ai_valid = True

                    if is_stress_ai_valid:
                        display_stress_title = clean_and_translate_to_english(stress_task_raw.get('title', 'Stress Management Task'))
                        if not stress_task_raw.get('title', '').startswith("[DEFAULT]"):
                            display_stress_title = f"✨ {display_stress_title}"

                        stress_task_html_rendered = f"""
                        <div class='stress-task-container'>
                            <h4><strong>{display_stress_title}</strong> {get_random_emoji("stress", st.session_state.holistic_user_data["Goal"])}</h4>
                            {format_task_section(
                                stress_task_raw.get("title", "Stress Management Task"),
                                stress_task_raw.get("description", AI_PLACEHOLDER_TEXT),
                                stress_task_raw.get("benefit", AI_PLACEHOLDER_TEXT),
                                stress_task_raw.get("pro_tips", AI_PLACEHOLDER_TEXT),
                                get_random_emoji("stress", st.session_state.holistic_user_data["Goal"]),
                                is_ai_generated_valid=True
                            )}
                        </div>
                        """
                    else:
                        stress_default_content = get_personalized_default_content("stress_task", st.session_state.holistic_user_data["Goal"], st.session_state.holistic_user_data, is_full_fallback=True)
                        stress_task_html = f"""
                        <div class='stress-task-container'>
                            <h4><strong>{stress_default_content['title']}</strong> {stress_default_content['emoji']}</h4>
                            {format_task_section(
                                stress_default_content['title'],
                                stress_default_content['description'],
                                stress_default_content['benefit'],
                                stress_default_content['pro_tips'],
                                stress_default_content['emoji'],
                                is_ai_generated_valid=False
                            )}
                        </div>
                        """

                    if is_habit_ai_valid:
                        display_habit_title = clean_and_translate_to_english(habit_task_raw.get('title', 'Habit Building Task'))
                        if not habit_task_raw.get('title', '').startswith("[DEFAULT]"):
                            display_habit_title = f"✨ {display_habit_title}"

                        habit_task_html_rendered = f"""
                        <div class='habit-task-container'>
                            <h4><strong>{display_habit_title}</strong> {get_random_emoji("habit", st.session_state.holistic_user_data["Goal"])}</h4>
                            {format_task_section(
                                habit_task_raw.get("title","Habit Building Task"),
                                habit_task_raw.get("description", AI_PLACEHOLDER_TEXT),
                                habit_task_raw.get("benefit", AI_PLACEHOLDER_TEXT),
                                habit_task_raw.get("pro_tips", AI_PLACEHOLDER_TEXT),
                                get_random_emoji("habit", st.session_state.holistic_user_data["Goal"]),
                                is_ai_generated_valid=True
                            )}
                        </div>
                        """
                    else:
                        habit_default_content = get_personalized_default_content("habit_task", st.session_state.holistic_user_data["Goal"], st.session_state.holistic_user_data, is_full_fallback=True)
                        habit_task_html = f"""
                        <div class='habit-task-container'>
                            <h4><strong>{habit_default_content['title']}</strong> {habit_default_content['emoji']}</h4>
                            {format_task_section(
                                habit_default_content['title'],
                                habit_default_content['description'],
                                habit_default_content['benefit'],
                                habit_default_content['pro_tips'],
                                habit_default_content['emoji'],
                                is_ai_generated_valid=False
                            )}
                        </div>
                        """

                except Exception as rendering_error:
                    logging.error(f"Error during rendering/fallback for Day {day_num}: {rendering_error}. Falling back to full default content for this day")
                    stress_default = get_personalized_default_content("stress_task", st.session_state.holistic_user_data["Goal"], st.session_state.holistic_user_data, is_full_fallback=True)
                    stress_task_html_rendered = f"""
                    <div class='stress-task-container'>
                        <h4><strong>{stress_default['title']}</strong> {stress_default['emoji']}</h4>
                        {format_task_section(stress_default['title'], stress_default['description'], stress_default['benefit'], stress_default['pro_tips'], stress_default['emoji'], is_ai_generated_valid=False)}
                    </div>
                    """
                    habit_default = get_personalized_default_content("habit_task", st.session_state.holistic_user_data["Goal"], st.session_state.holistic_user_data, is_full_fallback=True)
                    habit_task_html_rendered = f"""
                    <div class='habit-task-container'>
                        <h4><strong>{habit_default['title']}</strong> {habit_default['emoji']}</h4>
                        {format_task_section(habit_default['title'], habit_default['description'], habit_default['benefit'], habit_default['pro_tips'], habit_default['emoji'], is_ai_generated_valid=False)}
                    </div>
                    """

                with st.expander(f"🗓️ {day_title}", expanded=True):
                    st.markdown(stress_task_html_rendered, unsafe_allow_html=True)
                    st.markdown(habit_task_html_rendered, unsafe_allow_html=True)

            # Progress Tracking Section
            st.markdown("<h3>📈 Track Your Progress <span class='emoji-pulse'>✅</span></h3>", unsafe_allow_html=True)
            sorted_days_for_progress = sorted(st.session_state.progress.keys(), key=lambda x: int(x.split()[1]) if ' ' in x else float('inf'))

            consecutive_days = 0
            for day in sorted_days_for_progress:
                day_progress = st.session_state.progress.get(day, {})
                if day_progress.get("Stress", False) and day_progress.get("Habit", False):
                    consecutive_days += 1
                else:
                    break
            if consecutive_days >= 3:
                st.markdown(f"<div class='result-box'>🎉 You've completed {consecutive_days} days in a row! Keep it up! 🚀</div>", unsafe_allow_html=True)

            for day in sorted_days_for_progress:
                with st.container():
                    st.markdown(f"<div class='task-card'><strong>{day} 🗓️</strong></div>", unsafe_allow_html=True)
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Stress Task** 😌: Complete your daily stress management task")
                        st.markdown(f"**Habit Task** 🌱: Complete your daily habit-building task")

                    with col2:
                        stress_completed_key = f"stress_cb_{day}"
                        habit_completed_key = f"habit_cb_{day}"
                        value_ni_key = f"value_ni_{day}"

                        if day not in st.session_state.progress:
                            st.session_state.progress[day] = {"Stress": False, "Habit": False}
                        if day not in st.session_state.habit_values:
                            st.session_state.habit_values[day] = 0.0

                        st.session_state.progress[day]["Stress"] = st.checkbox("Stress Done ✅", key=stress_completed_key, value=st.session_state.progress[day].get("Stress", False))
                        st.session_state.progress[day]["Habit"] = st.checkbox("Habit Done ✅", key=habit_completed_key, value=st.session_state.progress[day].get("Habit", False))

                        completion_habit_value_for_display = 0.0

                        if st.session_state.holistic_user_data and st.session_state.holistic_user_data["Goal"] in ["Increase Water Intake", "Eat More Vegetables"]:
                            default_val = st.session_state.habit_values.get(day, 0.0)
                            if value_ni_key not in st.session_state or st.session_state[value_ni_key] is None:
                                st.session_state[value_ni_key] = default_val

                            current_value = st.number_input(
                                f"Value ({'Liters' if st.session_state.holistic_user_data['Goal'] == 'Increase Water Intake' else 'Servings/Day'})",
                                min_value=0.0, step=0.1, value=st.session_state[value_ni_key], key=value_ni_key
                            )
                            st.session_state.habit_values[day] = current_value

                            water_target = 2.0
                            veg_target = 3.0
                            if st.session_state.holistic_user_data["Goal"] == "Increase Water Intake":
                                if current_value >= water_target: completion_habit_value_for_display = 1.0
                                elif current_value > 0: completion_habit_value_for_display = 0.5
                            else: # Eat More Vegetables
                                if current_value >= veg_target: completion_habit_value_for_display = 1.0
                                elif current_value > 0: completion_habit_value_for_display = 0.5
                        else:
                            completion_habit_value_for_display = 1.0 if st.session_state.progress[day].get("Habit", False) else 0.0

                        num_tasks_to_consider = 0
                        total_completion_points = 0.0

                        if st.session_state.progress[day].get("Stress", False):
                            num_tasks_to_consider += 1
                            total_completion_points += 1.0
                        if st.session_state.progress[day].get("Habit", False):
                            num_tasks_to_consider += 1
                            total_completion_points += completion_habit_value_for_display

                        completion_percentage = (total_completion_points / num_tasks_to_consider * 100) if num_tasks_to_consider > 0 else 0.0
                        st.markdown(f"<div class='progress-bar'><div class='progress-fill' style='width: {completion_percentage:.2f}%'></div></div>", unsafe_allow_html=True)
                        st.markdown(f"**Completion**: {completion_percentage:.0f}%")

            # Visualize progress
            st.markdown("<h3>📊 Wellness Plan Progress</h3>", unsafe_allow_html=True)
            sorted_days_for_progress = sorted(st.session_state.progress.keys(), key=lambda x: int(x.split()[1]) if ' ' in x else float('inf'))

            progress_data_list = []
            for day in sorted_days_for_progress:
                stress_done = st.session_state.progress.get(day, {}).get("Stress", False)
                habit_done_checkbox = st.session_state.progress.get(day, {}).get("Habit", False)

                habit_completion_value_for_viz = 0.0
                if st.session_state.holistic_user_data and st.session_state.holistic_user_data["Goal"] in ["Increase Water Intake", "Eat More Vegetables"]:
                    if habit_done_checkbox:
                        current_value = st.session_state.habit_values.get(day, 0.0)
                        water_target = 2.0
                        veg_target = 3.0
                        if st.session_state.holistic_user_data["Goal"] == "Increase Water Intake":
                            if current_value >= water_target: habit_completion_value_for_viz = 1.0
                            elif current_value > 0: habit_completion_value_for_viz = 0.5
                        elif st.session_state.holistic_user_data["Goal"] == "Eat More Vegetables":
                            if current_value >= veg_target: habit_completion_value_for_viz = 1.0
                            elif current_value > 0: habit_completion_value_for_viz = 0.5
                else:
                    habit_completion_value_for_viz = 1.0 if habit_done_checkbox else 0.0

                progress_data_list.append({
                    "Day": day,
                    "Stress Task": 1.0 if stress_done else 0.0,
                    "Habit Task": habit_completion_value_for_viz
                })

            progress_data = pd.DataFrame(progress_data_list)
            if not progress_data.empty:
                fig = px.bar(
                    progress_data.melt(id_vars="Day", var_name="Task Type", value_name="Completion"),
                    x="Day", y="Completion", color="Task Type",
                    title="Your Wellness Progress 📊",
                    labels={"Completion": "Completion Status"},
                    barmode="stack", color_discrete_sequence=["#3b82f6", "#10b981"],
                    template="plotly_white"
                )
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No progress data available yet.")

            # Visualize daily goal value if applicable
            if st.session_state.holistic_user_data and st.session_state.holistic_user_data["Goal"] in ["Increase Water Intake", "Eat More Vegetables"]:
                st.markdown("<h3>📈 Daily Goal Tracking</h3>", unsafe_allow_html=True)
                value_data_list = []
                for day in sorted_days_for_progress:
                    value_data_list.append({
                        "Day": day,
                        "Value": st.session_state.habit_values.get(day, 0.0)
                    })
                value_data = pd.DataFrame(value_data_list)
                if not value_data.empty:
                    target_value = 2.0 if st.session_state.holistic_user_data["Goal"] == "Increase Water Intake" else 3.0
                    target_unit = "Liters" if st.session_state.holistic_user_data["Goal"] == "Increase Water Intake" else "Servings/Day"
                    fig = px.line(
                        value_data,
                        x="Day", y="Value",
                        title=f"Daily {st.session_state.holistic_user_data['Goal']} 📈",
                        labels={"Value": target_unit},
                        color_discrete_sequence=["#10b981"]
                    )
                    fig.add_hline(y=target_value, line_dash="dash", line_color="#ef4444", annotation_text=f"Target ({target_value} {target_unit})", annotation_position="top right")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No goal value data available yet.")

            # Stress Factors 3D Scatter Plot
            st.markdown("<h3>🌟 Stress Factors Analysis</h3>", unsafe_allow_html=True)
            with st.expander("📝 How to Interpret This 3D Visualization 📊"):
                st.markdown("""
                    <h4>Scientific Rationale</h4>
                    This 3D scatter plot visualizes the interplay between key stress-influencing factors: <strong>Workload Intensity</strong>, <strong>Social Support</strong>, and <strong>Relaxation Time</strong>. Each point's color represents the simulated or self-reported stress level, providing a multidimensional perspective on well-being. This approach is grounded in psychophysiological research linking environmental demands, social resources, and restorative activities to an individual's stress response.

                    <h4>Interpretation Guide</h4>
                    <ul style="list-style-type: disc; padding-left: 2rem;">
                        <li><strong>X-Axis (Workload Intensity)</strong>: Depicts the perceived demand of your daily tasks, scaled from 1 (Low) to 3 (High).</li>
                        <li><strong>Y-Axis (Social Support)</strong>: Represents the level of support received from your network, scaled inversely from 1 (High Support) to 3 (Low Support).</li>
                        <li><strong>Z-Axis (Relaxation Time)</strong>: Illustrates the time dedicated to restorative activities, normalized on a scale from 0 (minimal) to 3 (substantial).</li>
                        <li><strong>Color Gradient</strong>: Indicates the stress level, ranging from Green (Low Stress) through Yellow (Moderate Stress) to Purple (High Stress). Clusters in purple highlight areas where interventions might be most beneficial.</li>
                    </ul>
                    <p>Analyze the distribution of points to identify how your current situation might be contributing to stress and to inform strategies for improvement, such as adjusting workload, enhancing social connections, or prioritizing relaxation. 🔍</p>
                """, unsafe_allow_html=True)

            local_data = st.session_state.holistic_user_data
            scatter_data_list = []
            workload_map = {"Low": 1, "Moderate": 2, "High": 3}
            support_map = {"Low": 3, "Moderate": 2, "High": 1}
            stress_map = {"Low": 1, "Moderate": 2, "High": 3}

            if local_data:
                user_wl_val = workload_map.get(local_data["Workload_Intensity"], 2)
                user_supp_val = support_map.get(local_data["Social_Support"], 2)
                # Normalize relaxation time to a scale of 0-3 for visualization
                max_possible_relaxation = 8.0 # Assuming 8 hours as a theoretical max for normalization
                user_relax_val = min(local_data["Relaxation_Time"] / max_possible_relaxation * 3, 3) if local_data["Relaxation_Time"] is not None else 0.0
                user_stress_level_num = stress_map.get(local_data["Stress_Level"], 2)

                scatter_data_list.append({
                    "Workload Intensity": user_wl_val + random.uniform(-0.15, 0.15),
                    "Social Support": user_supp_val + random.uniform(-0.15, 0.15),
                    "Relaxation Time": user_relax_val + random.uniform(-0.15, 0.15),
                    "Stress Level": user_stress_level_num,
                    "Point Type": "Your Profile"
                })

            num_sample_points = 50
            for i in range(num_sample_points):
                sl_num = random.choice([1, 2, 3])
                scatter_data_list.append({
                    "Workload Intensity": random.uniform(0.7, 3.3),
                    "Social Support": random.uniform(0.7, 3.3),
                    "Relaxation Time": random.uniform(-0.3, 3.3), # Allow slightly negative for visual spread
                    "Stress Level": sl_num,
                    "Point Type": "Sample"
                })

            scatter_data = pd.DataFrame(scatter_data_list)

            fig = px.scatter_3d(
                scatter_data,
                x="Workload Intensity",
                y="Social Support",
                z="Relaxation Time",
                color="Stress Level",
                color_continuous_scale=[(0, "#66cc99"), (0.5, "#cccc66"), (1, "#cc6699")],
                size="Stress Level",
                size_max=12,
                opacity=0.8,
                title="Stress Factors 3D Analysis 🌟",
                labels={
                    "Workload Intensity": "Workload Intensity (1=Low, 3=High)",
                    "Social Support": "Social Support (1=High, 3=Low)",
                    "Relaxation Time": "Relaxation Time (Normalized 0-3)"
                },
                category_orders={"Stress Level": [1, 2, 3]}
            )

            if local_data:
                fig.update_traces(marker=dict(size=10, symbol='diamond', color='white', line=dict(color='black', width=2), opacity=1.0), selector=dict(name="Your Profile"))
            fig.update_traces(marker=dict(size=4, opacity=0.7), selector=dict(name="Sample"))

            fig.update_layout(
                scene=dict(
                    xaxis=dict(title="Workload Intensity", range=[0.5, 3.5], tickvals=[1, 2, 3], ticktext=["Low", "Moderate", "High"]),
                    yaxis=dict(title="Social Support", range=[0.5, 3.5], tickvals=[1, 2, 3], ticktext=["High", "Moderate", "Low"]),
                    zaxis=dict(title="Relaxation Time", range=[-0.5, 3.5]),
                    bgcolor="rgba(0,0,0,0)"
                ),
                font=dict(size=12),
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="center", x=0.5),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=50, r=50, t=100, b=50)
            )
            st.plotly_chart(fig, use_container_width=True)


# --- Helper function to format task sections ---
def format_task_section(title, description, benefit, tip, emoji_char, is_ai_generated_valid=True):
    html_parts = []
    cleaned_title = clean_and_translate_to_english(title)
    display_title = cleaned_title if cleaned_title else "Untitled Task"

    # Ensure placeholder text is used if the original content is deemed invalid or insufficient
    display_description = description if description and description.strip() and description != AI_PLACEHOLDER_TEXT else AI_PLACEHOLDER_TEXT
    display_benefit = benefit if benefit and benefit.strip() and benefit != AI_PLACEHOLDER_TEXT else AI_PLACEHOLDER_TEXT
    display_tip = tip if tip and tip.strip() and tip != AI_PLACEHOLDER_TEXT else AI_PLACEHOLDER_TEXT

    # Add emoji only if AI generated valid content, otherwise rely on default
    final_emoji = emoji_char if is_ai_generated_valid else ""
    final_display_title = f" {display_title}" if not title.startswith("[DEFAULT]") else display_title

    # Format with bolding and ensure proper spacing and punctuation
    formatted_description = clean_and_translate_to_english(f"Description: {display_description}")
    formatted_benefit = clean_and_translate_to_english(f"Benefit: {display_benefit}")
    formatted_tip = clean_and_translate_to_english(f"Pro Tip: {display_tip}")

    html_parts.append(f"<div>{formatted_description}</div>")
    html_parts.append(f"<div>{formatted_benefit}</div>")
    html_parts.append(f"<div>{formatted_tip}</div>")

    return "".join(html_parts)