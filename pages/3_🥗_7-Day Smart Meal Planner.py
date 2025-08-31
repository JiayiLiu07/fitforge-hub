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
    "Oats & Berries Bowl": "https://www.google.com/imgres?q=ats%20%26%20Berries%20Bowl&imgurl=https%3A%2F%2Fimg.taste.com.au%2FHF2K6LfF%2Ftaste%2F2016%2F11%2Foat-and-berry-acai-bowl-104111-1.jpeg&imgrefurl=https%3A%2F%2Fwww.taste.com.au%2Frecipes%2Foat-berry-acai-bowl%2Faf1dd66f-80bc-4b37-bfa5-f226610e061c&docid=dOdGzwFmynv4NM&tbnid=buCb6h7tNK3eSM&vet=12ahUKEwi1jNuJgLWPAxW8UvUHHV3TE78QM3oECB8QAA..i&w=3000&h=2000&hcb=2&ved=2ahUKEwi1jNuJgLWPAxW8UvUHHV3TE78QM3oECB8QAA",
    "Egg & Avocado Toast": "https://www.google.com/imgres?q=Egg%20%26%20Avocado%20Toast&imgurl=https%3A%2F%2Fwww.allrecipes.com%2Fthmb%2FKy6yT_-juhi_bO8OPI2ZL9cXojc%3D%2F1500x0%2Ffilters%3Ano_upscale()%3Amax_bytes(150000)%3Astrip_icc()%2FAvocadoToastwithEggFranceC2x1-d73da05afae3436fa9b0b72430fab3d6.jpg&imgrefurl=https%3A%2F%2Fwww.allrecipes.com%2Frecipe%2F265304%2Favocado-toast-with-egg%2F&docid=XWl51lDbENBltM&tbnid=INTYnn7dY4zkGM&vet=12ahUKEwjc7JWVgLWPAxW2k68BHXodOn8QM3oECBcQAA..i&w=1500&h=750&hcb=2&ved=2ahUKEwjc7JWVgLWPAxW2k68BHXodOn8QM3oECBcQAA0",
    "Greek Yogurt Parfait": "https://www.google.com/imgres?q=Greek%20Yogurt%20Parfait&imgurl=https%3A%2F%2Fwww.homemadefoodjunkie.com%2Fwp-content%2Fuploads%2F2021%2F07%2FUntitled-design-84.jpg&imgrefurl=https%3A%2F%2Fwww.homemadefoodjunkie.com%2Fgreek-yogurt-parfait%2F&docid=QoiCcG-P8TFfRM&tbnid=LqQoPbt_wml-jM&vet=12ahUKEwjZ_4C5gLWPAxXVbvUHHeNuGT8QM3oECCQQAA..i&w=1500&h=1000&hcb=2&ved=2ahUKEwjZ_4C5gLWPAxXVbvUHHeNuGT8QM3oECCQQAA",
    "Grilled Chicken Salad": "https://www.google.com/imgres?q=grilled%20chicken%20salad&imgurl=https%3A%2F%2Fwww.simplyrecipes.com%2Fthmb%2FKFI2R9ZgZag1tUPFKXgTBEoblIg%3D%2F1500x0%2Ffilters%3Ano_upscale()%3Amax_bytes(150000)%3Astrip_icc()%2FSImply-Recipes-Grilled-Chicken-Greek-Salad-LEAD-2-f4854b96ee4d4da08d8155de3c7454b8.jpg&imgrefurl=https%3A%2F%2Fwww.simplyrecipes.com%2Fgreek-grilled-chicken-salad-recipe-11746322&docid=Te1F_X-5B7pxEM&tbnid=i-gBw_dommDmIM&vet=12ahUKEwif6sPogLWPAxU8oq8BHRirCwsQM3oECCgQAA..i&w=1500&h=1000&hcb=2&ved=2ahUKEwif6sPogLWPAxU8oq8BHRirCwsQM3oECCgQAA",
    "Tofu Stir-fry": "https://www.google.com/imgres?q=Tofu%20Stir-fry&imgurl=https%3A%2F%2Fheatherchristo.com%2Fwp-content%2Fuploads%2F2020%2F02%2F49580825886_3bb8047334_o-scaled.jpg&imgrefurl=https%3A%2F%2Fheatherchristo.com%2F2020%2F02%2F24%2Fcrispy-tofu-basil-stir-fry%2F&docid=qqrgttks-NRq5M&tbnid=HCOhT5dbxsjt_M&vet=12ahUKEwjs3IWjgbWPAxVTkq8BHY-aAzAQM3oECC8QAA..i&w=2560&h=1707&hcb=2&ved=2ahUKEwjs3IWjgbWPAxVTkq8BHY-aAzAQM3oECC8QAA",
    "Quinoa Salad": "https://www.google.com/imgres?q=Quinoa%20Salad&imgurl=https%3A%2F%2Fimages.themodernproper.com%2Fproduction%2Fposts%2FQuinoaSalad_9.jpg%3Fw%3D960%26h%3D960%26q%3D82%26fm%3Djpg%26fit%3Dcrop%26dm%3D1739653270%26s%3D19c15d2fbe8a13e80443bd959a547b39&imgrefurl=https%3A%2F%2Fthemodernproper.com%2Fquinoa-salad&docid=wLZytgjOhPQ_OM&tbnid=nsuJKLfuqF8JUM&vet=12ahUKEwj78patgbWPAxWpcvUHHUCjG9UQM3oECCgQAA..i&w=960&h=960&hcb=2&ved=2ahUKEwj78patgbWPAxWpcvUHHUCjG9UQM3oECCgQAA",
    "Baked Cod & Veg": "https://www.google.com/imgres?q=Baked%20Cod%20%26%20Veg&imgurl=https%3A%2F%2Fyoungsseafood.co.uk%2Fwp-content%2Fuploads%2F2015%2F04%2FCod-Fillets-Roasted-Veg-Sauce-Vierge.jpg&imgrefurl=https%3A%2F%2Fyoungsseafood.co.uk%2Frecipes%2Fcod-fillets-roasted-vegetables-sauce-vierge%2F&docid=pMMq4HnjttVAFM&tbnid=00KaQAUx31aSZM&vet=12ahUKEwjW2o65gbWPAxXjga8BHbNDIQkQM3oECCAQAA..i&w=1400&h=600&hcb=2&ved=2ahUKEwjW2o65gbWPAxXjga8BHbNDIQkQM3oECCAQAA",
    "Lentil Curry": "https://www.google.com/imgres?q=Lentil%20Curry&imgurl=https%3A%2F%2Fwww.noracooks.com%2Fwp-content%2Fuploads%2F2022%2F07%2Flentil-curry-7.jpg&imgrefurl=https%3A%2F%2Fwww.noracooks.com%2Flentil-curry%2F&docid=PMt72Jcp8_EiyM&tbnid=EAcvnIo0MEWE6M&vet=12ahUKEwj3-v7EgbWPAxX8ma8BHU2lOoIQM3oECBgQAA..i&w=1334&h=1334&hcb=2&ved=2ahUKEwj3-v7EgbWPAxX8ma8BHU2lOoIQM3oECBgQAA",
    "Grilled Salmon": "https://www.google.com/imgres?q=Grilled%20Salmo&imgurl=https%3A%2F%2Fwww.thespruceeats.com%2Fthmb%2FHgM2h42z1HGEcSWkWk5CgAjDDpQ%3D%2F1500x0%2Ffilters%3Ano_upscale()%3Amax_bytes(150000)%3Astrip_icc()%2Fhow-to-grill-salmon-2216658-hero-01-a9c948f8a238400ebaafc0caf509c7fa.jpg&imgrefurl=https%3A%2F%2Fwww.thespruceeats.com%2Fhow-to-grill-salmon-2216658&docid=-l1ILQpHN2uOXM&tbnid=qfUxsKbPOpEFGM&vet=12ahUKEwi0pfLRgbWPAxWAg68BHS08HkUQM3oECCYQAA..i&w=1500&h=1001&hcb=2&ved=2ahUKEwi0pfLRgbWPAxWAg68BHS08HkUQM3oECCYQAA",
    "Greek Yogurt with Berries": "https://www.google.com/imgres?q=Greek%20Yogurt%20with%20Berries&imgurl=https%3A%2F%2Fusa.fage%2Fsites%2Fusa.fage%2Ffiles%2FFage_Recipe_Tiles_B_600x420_Apr21_Plain_Loaded_BowlsA_Hero_1291_RGB.jpg&imgrefurl=https%3A%2F%2Fusa.fage%2Frecipes%2Fgreek-yogurt-recipes%2Fmixed-berry-yogurt-bowl&docid=M0OOvEb5-jkAPM&tbnid=mvF76oCGAQphlM&vet=12ahUKEwjJwOncgbWPAxW2j68BHSAiFy0QM3oECBgQAA..i&w=600&h=420&hcb=2&ved=2ahUKEwjJwOncgbWPAxW2j68BHSAiFy0QM3oECBgQAA",
    "Grilled Chicken Quinoa Bowl": "https://www.google.com/imgres?q=Grilled%20Chicken%20Quinoa%20Bowl&imgurl=https%3A%2F%2Ffood.fnr.sndimg.com%2Fcontent%2Fdam%2Fimages%2Ffood%2Ffullset%2F2020%2F03%2F06%2FWU2412__chicken-quinoa-bowl_s4x3.jpg.rend.hgtvcom.1280.960.suffix%2F1583516899411.webp&imgrefurl=https%3A%2F%2Fwww.foodnetwork.com%2Frecipes%2Free-drummond%2Fchicken-quinoa-bowl-8356446&docid=wbFXFOoOKZBUOM&tbnid=mE9C8ikPLzzdjM&vet=12ahUKEwiHyLzngbWPAxWKga8BHV_EI7gQM3oECBsQAA..i&w=1280&h=960&hcb=2&ved=2ahUKEwiHyLzngbWPAxWKga8BHV_EI7gQM3oECBsQAA",
    "Baked Salmon with Sweet Potato": "https://www.google.com/imgres?q=Baked%20Salmon%20with%20Sweet%20Potato&imgurl=https%3A%2F%2Fwww.hwcmagazine.com%2Fwp-content%2Fuploads%2F2018%2F01%2FIMG_8216.jpg&imgrefurl=https%3A%2F%2Fwww.hwcmagazine.com%2Frecipe%2Fbaked-spicy-salmon-sweet-potato-kale-hash%2F&docid=cCIcJ8SnFXO80M&tbnid=wZBnclNJexaPvM&vet=12ahUKEwipuOzugbWPAxX5a_UHHUyGAgsQM3oECCcQAA..i&w=700&h=525&hcb=2&ved=2ahUKEwipuOzugbWPAxX5a_UHHUyGAgsQM3oECCcQAA",
    "Veggie Omelette": "https://www.google.com/imgres?q=Veggie%20Omelette&imgurl=https%3A%2F%2Fjoybauer.com%2Fwp-content%2Fuploads%2F2016%2F02%2Fegg-veggie-omelet-1.jpg&imgrefurl=https%3A%2F%2Fjoybauer.com%2Fhealthy-recipes%2Ffiesta-vegetable-omelet%2F&docid=SgB57ftT9vU_SM&tbnid=J_98mNgG9-J1gM&vet=12ahUKEwjc_oeVgrWPAxVUna8BHWD-DMMQM3oECB4QAA..i&w=1000&h=667&hcb=2&ved=2ahUKEwjc_oeVgrWPAxVUna8BHWD-DMMQM3oECB4QAA",
    "Lentil Salad with Tuna": "https://www.google.com/imgres?q=Lentil%20Salad%20with%20Tuna&imgurl=https%3A%2F%2Fgirlheartfood.com%2Fwp-content%2Fuploads%2F2021%2F12%2FTuna-Lentil-Salad-2.jpg&imgrefurl=https%3A%2F%2Fgirlheartfood.com%2Fmediterranean-lentil-salad%2F&docid=aEGRTyAR_ucm-M&tbnid=4m9wB4txKP4w5M&vet=12ahUKEwjho6CfgrWPAxVPSfUHHS6TGiEQM3oECB0QAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwjho6CfgrWPAxVPSfUHHS6TGiEQM3oECB0QAA",
    "Turkey Stir Fry": "https://www.google.com/imgres?q=Turkey%20Stir%20Fry&imgurl=https%3A%2F%2Flemonsandzest.com%2Fwp-content%2Fuploads%2F2020%2F11%2FGround-Turkey-Teriyaki-2.15.jpg&imgrefurl=https%3A%2F%2Flemonsandzest.com%2Fground-turkey-teriyaki-stir-fry%2F&docid=-F8SrAftNkvaVM&tbnid=STpgRV1hoF3VQM&vet=12ahUKEwiwxaOrgrWPAxVIa_UHHYAfDf0QM3oECB4QAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwiwxaOrgrWPAxVIa_UHHYAfDf0QM3oECB4QAA",
    "Smoothie Bowl": "https://www.google.com/imgres?q=Smoothie%20Bowl&imgurl=https%3A%2F%2Fhealthfulblondie.com%2Fwp-content%2Fuploads%2F2022%2F06%2FHomemade-Healthy-Protein-Acai-Bowl.jpg&imgrefurl=https%3A%2F%2Fhealthfulblondie.com%2Fbest-homemade-acai-bowl%2F&docid=X2E3IqrkPvz9WM&tbnid=4C7KijXJumWkCM&vet=12ahUKEwjokOa5grWPAxVTZ_UHHdCuJ5EQM3oFCIEBEAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwjokOa5grWPAxVTZ_UHHdCuJ5EQM3oFCIEBEAA",
    "Whole Wheat Turkey Wrap": "https://www.google.com/imgres?q=Whole%20Wheat%20Turkey%20Wrap&imgurl=https%3A%2F%2Fcorp.commissaries.com%2Fsites%2Fdefault%2Ffiles%2Fstyles%2Frecipe_node_image%2Fpublic%2F2021-06%2FTurkey%2520and%2520Avocado%2520Wrap%2520with%2520Red%2520Pepper%2520Hummus.png%3Fitok%3DifEt62fY&imgrefurl=https%3A%2F%2Fcorp.commissaries.com%2Frecipes%2Fturkey-and-avocado-wrap-red-pepper-hummus&docid=GsqIICYI2DFt0M&tbnid=QbQONChDSXsvuM&vet=12ahUKEwj08MvKgrWPAxV1dfUHHWK3GykQM3oECDAQAA..i&w=800&h=600&hcb=2&ved=2ahUKEwj08MvKgrWPAxV1dfUHHWK3GykQM3oECDAQAA",
    "Zucchini Noodles": "https://www.google.com/imgres?q=Zucchini%20Noodles&imgurl=https%3A%2F%2Fwww.jessicagavin.com%2Fwp-content%2Fuploads%2F2018%2F05%2Fzucchini-noodles-5-1200.jpg&imgrefurl=https%3A%2F%2Fwww.jessicagavin.com%2Fhow-to-make-zucchini-noodles%2F&docid=GxzAsHiLOqCYhM&tbnid=nWNYqdy4BWwdHM&vet=12ahUKEwiH19DUgrWPAxWpc_UHHe4yF8YQM3oECCwQAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwiH19DUgrWPAxWpc_UHHe4yF8YQM3oECCwQAA",
    "Chickpea and Spinach Curry": "https://www.google.com/imgres?q=Chickpea%20and%20Spinach%20Curry&imgurl=https%3A%2F%2Fthefoodiephysician.com%2Fwp-content%2Fuploads%2F2014%2F10%2Fchickpea-curry-500x375.jpg&imgrefurl=https%3A%2F%2Fthefoodiephysician.com%2Fchickpea-and-spinach-curry%2F&docid=f515JgRsGBobzM&tbnid=WYUd5P-jmeMjIM&vet=12ahUKEwi919fggrWPAxXTrq8BHSpJHRwQM3oECCkQAA..i&w=500&h=375&hcb=2&ved=2ahUKEwi919fggrWPAxXTrq8BHSpJHRwQM3oECCkQAA",
    "Stuffed Bell Peppers": "https://www.google.com/imgres?q=Stuffed%20Bell%20Peppers&imgurl=https%3A%2F%2Fwww.allrecipes.com%2Fthmb%2FeBsB2933MCuNVCim4O-AyCR97YE%3D%2F1500x0%2Ffilters%3Ano_upscale()%3Amax_bytes(150000)%3Astrip_icc()%2F79805-StuffedPeppersWithturkeyAndVegtables-MFS-2x3-0048-444ecb49b0184daab29e5326e4330af3.jpg&imgrefurl=https%3A%2F%2Fwww.allrecipes.com%2Frecipe%2F79805%2Fstuffed-peppers-with-turkey-and-vegetables%2F&docid=x9GO3_EaC46ymM&tbnid=plO5-afXFYis9M&vet=12ahUKEwjHvcHsgrWPAxXjnq8BHRMZFuYQM3oECCEQAA..i&w=1500&h=1125&hcb=2&ved=2ahUKEwjHvcHsgrWPAxXjnq8BHRMZFuYQM3oECCEQAA",
    "Cottage Cheese with Fruit": "https://www.google.com/imgres?q=Cottage%20Cheese%20with%20Fruit&imgurl=https%3A%2F%2Fwww.midwestliving.com%2Fthmb%2FV97-U0Bub42Oe0gewPJh2lIA_hE%3D%2F1500x0%2Ffilters%3Ano_upscale()%3Amax_bytes(150000)%3Astrip_icc()%2FPASSANO_MWL0621_KeyIng_CottageCheese_Salad_8544_preview-dd1d0cff26494514a2b92cf126f029e9.jpg&imgrefurl=https%3A%2F%2Fwww.midwestliving.com%2Frecipe%2Fbasil-fruit-salad-with-cottage-cheese%2F&docid=hT4AlJDnnBOIXM&tbnid=Az1Clzhvlt7uGM&vet=12ahUKEwiDg6r3grWPAxW5cfUHHRlZF_0QM3oECFQQAA..i&w=1500&h=1000&hcb=2&ved=2ahUKEwiDg6r3grWPAxW5cfUHHRlZF_0QM3oECFQQAA",
    "Tuna and Bean Salad": "https://www.google.com/imgres?q=Tuna%20and%20Bean%20Salad&imgurl=https%3A%2F%2Fxoxobella.com%2Fwp-content%2Fuploads%2F2023%2F05%2Fitalian_tuna_white_bean_salad_055.jpg&imgrefurl=https%3A%2F%2Fxoxobella.com%2Fitalian-tuna-white-bean-salad%2F&docid=YFpCVsj3gapqUM&tbnid=mIx2MAw792QU4M&vet=12ahUKEwig7-e8g7WPAxVQafUHHYNVEZIQM3oECBwQAA..i&w=1200&h=675&hcb=2&ved=2ahUKEwig7-e8g7WPAxVQafUHHYNVEZIQM3oECBwQAA",
    "Grilled Chicken with Veggies": "https://www.google.com/imgres?q=Grilled%20Chicken%20with%20Veggies&imgurl=https%3A%2F%2Frecipes.heart.org%2Fen%2F-%2Fmedia%2FAHA%2FRecipe%2FRecipe-Images%2FGrilled-Chicken-with-Vegetables-sized.jpg%3Fiar%3D0%26mw%3D890%26sc_lang%3Den&imgrefurl=https%3A%2F%2Frecipes.heart.org%2Fen%2Frecipes%2Fgrilled-chicken-with-vegetables&docid=26P1cVajGS9gXM&tbnid=z2F1Vfk2gmHAYM&vet=12ahUKEwj1i5bUg7WPAxXvc_UHHYs0E88QM3oECBkQAA..i&w=618&h=346&hcb=2&ved=2ahUKEwj1i5bUg7WPAxXvc_UHHYs0E88QM3oECBkQAA",
    "Overnight Oats": "https://www.google.com/imgres?q=Overnight%20Oats&imgurl=https%3A%2F%2Fthedeliciousplate.com%2Fwp-content%2Fuploads%2F2024%2F04%2FOvernight-oats-with-frozen-fruit-9.jpg&imgrefurl=https%3A%2F%2Fthedeliciousplate.com%2Fovernight-oats-with-frozen-fruit%2F&docid=Y29WTGeiYJAzEM&tbnid=vkU8FPFKTDw-JM&vet=12ahUKEwix0rrjg7WPAxXDsqgCHRm5IXwQM3oECGQQAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwix0rrjg7WPAxXDsqgCHRm5IXwQM3oECGQQAA",
    "Quinoa and Chickpea Salad": "https://www.google.com/imgres?q=Quinoa%20and%20Chickpea%20Salad&imgurl=https%3A%2F%2Fwww.eatwell101.com%2Fwp-content%2Fuploads%2F2021%2F02%2FHealthy-Chickpea-Quinoa-Salad-recipe-1-1200x800.jpg&imgrefurl=https%3A%2F%2Fwww.eatwell101.com%2Fchickpea-quinoa-salad-recipe&docid=T-A0AQ_sAOB17M&tbnid=ficWSiGgLoRmSM&vet=12ahUKEwjw_b3yg7WPAxU0fPUHHSo4FR8QM3oECB8QAA..i&w=1200&h=800&hcb=2&ved=2ahUKEwjw_b3yg7WPAxU0fPUHHSo4FR8QM3oECB8QAA",
    "Shrimp Stir Fry": "https://www.google.com/imgres?q=Shrimp%20Stir%20Fry&imgurl=https%3A%2F%2Fwww.jessicagavin.com%2Fwp-content%2Fuploads%2F2018%2F01%2Fshrimp-stir-fry7-1200.jpg&imgrefurl=https%3A%2F%2Fwww.jessicagavin.com%2Feasy-shrimp-stir-fry%2F&docid=ZdnUYK8rgaqeOM&tbnid=fDQeSAiHCKxjVM&vet=12ahUKEwj456SGhLWPAxVQafUHHYNVEZIQM3oECCEQAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwj456SGhLWPAxVQafUHHYNVEZIQM3oECCEQAA",
    "Egg and Veggie Scramble": "https://www.google.com/imgres?q=Egg%20and%20Veggie%20Scramble&imgurl=https%3A%2F%2Fmerryabouttown.com%2Fwp-content%2Fuploads%2F2014%2F01%2FEasy-Paleo-Breakfast-Messy-Egg-Bacon-and-Veggie-Scramble-720x540.jpg&imgrefurl=https%3A%2F%2Fmerryabouttown.com%2Fpaleo-breakfast-messy-egg-bacon-veggie-scramble%2F&docid=v-uHOHKkJI1v-M&tbnid=VD1DfQOMSo5fQM&vet=12ahUKEwifv9OShLWPAxW5sK8BHcRYGeQQM3oECCYQAA..i&w=720&h=540&hcb=2&ved=2ahUKEwifv9OShLWPAxW5sK8BHcRYGeQQM3oECCYQAA",
    "Lentil Soup": "https://www.google.com/imgres?q=Lentil%20Soup&imgurl=https%3A%2F%2Fwww.connoisseurusveg.com%2Fwp-content%2Fuploads%2F2023%2F12%2Fitalian-lentil-soup-sq-2.jpg&imgrefurl=https%3A%2F%2Fwww.connoisseurusveg.com%2Fitalian-lentil-soup%2F&docid=xjS-Fazy8AQl1M&tbnid=atWWyBd5Fvb8kM&vet=12ahUKEwihqNOdhLWPAxXDdfUHHS0lItAQM3oECCAQAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwihqNOdhLWPAxXDdfUHHS0lItAQM3oECCAQAA",
    "Baked Chicken Thighs": "https://www.google.com/imgres?q=Baked%20Chicken%20Thighs&imgurl=https%3A%2F%2Fdownshiftology.com%2Fwp-content%2Fuploads%2F2019%2F02%2FCrispy-Baked-Chicken-Thighs-main.jpg&imgrefurl=https%3A%2F%2Fdownshiftology.com%2Frecipes%2Fcrispy-baked-chicken-thighs%2F&docid=T8LHGEceug90yM&tbnid=AcynF33i2YwDtM&vet=12ahUKEwjwhaGxhLWPAxVKe_UHHYynNOMQM3oECCAQAA..i&w=1600&h=1067&hcb=2&ved=2ahUKEwjwhaGxhLWPAxVKe_UHHYynNOMQM3oECCAQAA",
    "Mediterranean Chickpea Bowl": "https://images.unsplash.com/photo-1505576391880-b3f9d713dc4f?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Vegetable Sushi Roll": "https://images.unsplash.com/photo-1579586337215-9c35e0017805?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Thai Green Curry": "https://images.unsplash.com/photo-1593504102882-3f28e1a4a591?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Baked Tofu with Veggies": "https://images.unsplash.com/photo-1528798834-c90d2b2b2606?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Falafel Wrap": "https://images.unsplash.com/photo-1604908812561-6bd1c0a49d8f?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Miso Soup with Tofu": "https://images.unsplash.com/photo-1604908812561-6bd1c0a49d8f?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Spaghetti Squash": "https://images.unsplash.com/photo-1603133872878-684f209f57b7?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Fallback Breakfast Dish": "https://images.unsplash.com/photo-1493770348161-369560ae357d?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Fallback Lunch Dish": "https://images.unsplash.com/photo-1546069901-ba9599a7e7ec?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
    "Fallback Dinner Dish": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120"
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
        if is_risk:
            if 'High' in factor['risk']:
                high_risk_count += 1
                total_risk_score += factor['weight']
            elif 'Medium' in factor['risk']:
                medium_risk_count += 1
                total_risk_score += factor['weight'] * 0.5
        
        risk_summary.append({
            'Risk Factor': factor['name'],
            'User Input': str(factor['value']),
            'Risk Level': risk_level
        })
    
    return pd.DataFrame(risk_summary), high_risk_count, medium_risk_count, total_risk_score

# API Key Check
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ Please enter a valid API key in the 🗣️ NL2SQL page.")
    st.stop()
try:
    client = OpenAI(
        api_key=st.session_state["api_key"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=60
    )
except AuthenticationError:
    logging.error("Failed to initialize OpenAI client: Invalid API key")
    st.error("⚠️ Invalid API key. Please verify your API key in the 🗣️ NL2SQL page and check the DashScope console (https://dashscope.aliyun.com/).")
    st.stop()
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    st.error(f"Failed to initialize API client: {e}. Please verify your API key in the 🗣️ NL2SQL page and check the DashScope console (https://dashscope.aliyun.com/).")
    st.stop()

# Generate Single Dish with Cache and Local DB Priority
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), retry=retry_if_exception_type(Exception))
def ai_generate_single_dish(obesity_level: str, user: dict, prefs, cuisine, difficulty, exclude, day: str, meal: str):
    cache_key = f"{obesity_level}_{meal}_{cuisine}_{difficulty}_{'_'.join(sorted(prefs))}_{'_'.join(sorted(exclude))}_{day}"
    if cache_key in st.session_state["dish_cache"]:
        logging.info(f"Using cached dish for {cache_key}")
        dish = st.session_state["dish_cache"][cache_key].copy()
        dish["day"] = day
        dish["meal"] = meal
        return dish

    # Try local database first
    available_dishes = []
    for dish_name, dish_data in RECIPE_DB.get(meal, {}).items():
        if meets_filter_criteria(dish_data, prefs, cuisine, difficulty, exclude):
            available_dishes.append((dish_name, dish_data))
    
    if available_dishes:
        import random
        dish_name, dish_data = random.choice(available_dishes)
        dish = {
            "day": day,
            "meal": meal,
            "dish": dish_name,
            "calories": dish_data["calories"],
            "protein": dish_data["protein"],
            "carbohydrates": dish_data["carbohydrates"],
            "fat": dish_data["fat"],
            "ingredients": dish_data["ingredients"],
            "steps": dish_data["steps"],
            "image_url": dish_data["image_url"],
            "is_fallback": True
        }
        st.session_state["dish_cache"][cache_key] = dish.copy()
        return dish

    dietary_constraints = []
    if "Vegetarian" in prefs:
        dietary_constraints.append("Must be vegetarian (no meat, fish, or poultry).")
    if "High-Protein" in prefs:
        dietary_constraints.append("Must prioritize high-protein ingredients (e.g., legumes, tofu, lean meats, eggs; at least 25g protein).")
    if "Low-Carb" in prefs:
        dietary_constraints.append("Must minimize carbohydrates (e.g., limit grains, starchy vegetables; max 40g carbs).")
    if "Gluten-Free" in prefs:
        dietary_constraints.append("Must exclude gluten-containing ingredients (e.g., wheat, barley, rye).")
    
    prompt = f"""
You are a nutritionist AI. Generate a unique single dish for obesity level "{obesity_level}" for {meal} on {day}.
User BMI: {user['weight']/user['height']**2:.1f}
Daily goals: 2000 kcal / 50 g protein / 200 g carbs / 70 g fat
Preferences: {', '.join(prefs) if prefs else 'None'}
Cuisine: {cuisine}
Difficulty: {difficulty}
Exclude ingredients: {', '.join(exclude) if exclude else 'None'}
Dietary constraints: {', '.join(dietary_constraints) if dietary_constraints else 'None'}

The dish must:
- Follow WHO nutrition guidelines for balanced macronutrients.
- Be tailored to the obesity level to promote healthy weight management.
- Strictly adhere to user preferences: {', '.join(prefs) if prefs else 'None'}.
- Match the specified cuisine: {cuisine}.
- Match the specified difficulty level: {difficulty} (e.g., Easy: minimal steps; Medium: moderate prep; Hard: complex techniques).
- Exclude specified ingredients: {', '.join(exclude) if exclude else 'None'}.
- Include a real image URL (from Unsplash or Pexels, 280x120 pixels) that exactly matches the dish name and description.
- Ensure the dish name and description are consistent with the provided image and avoid repetition with common dishes (e.g., no duplicates like 'Oats & Berries Bowl').
Return **ONLY** a valid JSON object with keys: day, meal, dish, calories, protein, carbohydrates, fat, ingredients, steps, image_url, is_fallback. Do not include any additional text or Markdown.
Example:
{{
  "day": "{day}",
  "meal": "{meal}",
  "dish": "Spicy Tofu Stir-fry",
  "calories": 350,
  "protein": 20,
  "carbohydrates": 30,
  "fat": 15,
  "ingredients": "Tofu, bell peppers, soy sauce, chili paste",
  "steps": "Stir-fry tofu and peppers with soy sauce and chili.",
  "image_url": "https://images.unsplash.com/photo-1528798834-c90d2b2b2606?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
  "is_fallback": false
}}
"""
    try:
        with st.spinner("Fetching AI-generated dish..."):
            resp = client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=120
            )
        response_text = resp.choices[0].message.content.strip()
        logging.debug(f"LLM prompt for single dish: {prompt}")
        logging.debug(f"LLM response for single dish: {response_text}")
        if not response_text:
            raise ValueError("Empty response from LLM")
        try:
            # Clean response
            response_text = re.sub(r'^```json\n|\n```$', '', response_text).strip()
            dish = json.loads(response_text)
            if not isinstance(dish, dict):
                raise ValueError("Invalid JSON structure: not a dictionary")
            required_keys = ["day", "meal", "dish", "calories", "protein", "carbohydrates", "fat", "ingredients", "steps", "image_url"]
            if not all(key in dish for key in required_keys):
                raise ValueError(f"Missing required JSON fields: {set(required_keys) - set(dish.keys())}")
            # Add is_fallback flag
            dish["is_fallback"] = False
            # Validate image URL
            is_valid = validate_image_url(dish["image_url"])
            if not is_valid:
                dish["image_url"] = FALLBACK_IMAGES.get(dish["dish"], FALLBACK_IMAGES[f"Fallback {meal} Dish"])
            # Cache the dish
            st.session_state["dish_cache"][cache_key] = dish.copy()
            return dish
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON format in single dish response: {e}. Raw response: {response_text}")
            st.error(f"Failed to parse dish response: Invalid JSON format ({e}). Using fallback dish.")
            dish = {
                "day": day,
                "meal": meal,
                "dish": f"Fallback {meal} Dish",
                "calories": 350,
                "protein": 15,
                "carbohydrates": 40,
                "fat": 10,
                "ingredients": "Generic ingredients",
                "steps": "Prepare as needed.",
                "image_url": FALLBACK_IMAGES[f"Fallback {meal} Dish"],
                "is_fallback": True
            }
            st.session_state["dish_cache"][cache_key] = dish.copy()
            return dish
    except Exception as e:
        logging.error(f"AI single dish generation failed: {e}. Raw response: {response_text if 'response_text' in locals() else 'None'}")
        st.error(f"Failed to generate dish: {e}. Using fallback dish.")
        dish = {
            "day": day,
            "meal": meal,
            "dish": f"Fallback {meal} Dish",
            "calories": 350,
            "protein": 15,
            "carbohydrates": 40,
            "fat": 10,
            "ingredients": "Generic ingredients",
            "steps": "Prepare as needed.",
            "image_url": FALLBACK_IMAGES[f"Fallback {meal} Dish"],
            "is_fallback": True
        }
        st.session_state["dish_cache"][cache_key] = dish.copy()
        return dish

# Generate 7-Day Meal Plan with Local DB Priority
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), retry=retry_if_exception_type(Exception))
def ai_generate_7day_plan(obesity_level: str, user: dict, prefs, cuisine, difficulty, exclude, base_date: datetime):
    cache_key = f"plan_{obesity_level}_{cuisine}_{difficulty}_{'_'.join(sorted(prefs))}_{'_'.join(sorted(exclude))}_{base_date.strftime('%Y-%m-%d')}"
    if cache_key in st.session_state["dish_cache"]:
        logging.info(f"Using cached meal plan for {cache_key}")
        df = st.session_state["dish_cache"][cache_key].copy()
        df["day"] = pd.Categorical(df["day"], categories=[(base_date + timedelta(days=i)).strftime("%a %m-%d") for i in range(7)], ordered=True)
        return df

    dietary_constraints = []
    if "Vegetarian" in prefs:
        dietary_constraints.append("Must be vegetarian (no meat, fish, or poultry).")
    if "High-Protein" in prefs:
        dietary_constraints.append("Must prioritize high-protein ingredients (e.g., legumes, tofu, lean meats, eggs; at least 25g protein).")
    if "Low-Carb" in prefs:
        dietary_constraints.append("Must minimize carbohydrates (e.g., limit grains, starchy vegetables; max 40g carbs).")
    if "Gluten-Free" in prefs:
        dietary_constraints.append("Must exclude gluten-containing ingredients (e.g., wheat, barley, rye).")
    
    prompt = f"""
You are a nutritionist AI. Create a 7-day meal plan (breakfast/lunch/dinner) for obesity level "{obesity_level}".
User BMI: {user['weight']/user['height']**2:.1f}
Start date: {base_date.strftime("%Y-%m-%d")}
Daily goals: 2000 kcal / 50 g protein / 200 g carbs / 70 g fat
Preferences: {', '.join(prefs) if prefs else 'None'}
Cuisine: {cuisine}
Difficulty: {difficulty}
Exclude ingredients: {', '.join(exclude) if exclude else 'None'}
Dietary constraints: {', '.join(dietary_constraints) if dietary_constraints else 'None'}

The meal plan must:
- Follow WHO nutrition guidelines for balanced macronutrients.
- Be tailored to the obesity level to promote healthy weight management.
- Strictly adhere to user preferences: {', '.join(prefs) if prefs else 'None'}.
- Match the specified cuisine: {cuisine}.
- Match the specified difficulty level: {difficulty} (e.g., Easy: minimal steps; Medium: moderate prep; Hard: complex techniques).
- Exclude specified ingredients: {', '.join(exclude) if exclude else 'None'}.
- Include a real image URL (from Unsplash or Pexels, 280x120 pixels) that exactly matches the dish name and description.
- Ensure the dish name and description are consistent with the provided image and avoid repetitive dishes.
- Provide a diverse set of dishes to enhance variety (e.g., different proteins, vegetables, cooking methods).
Return **ONLY** a valid JSON list with exactly 21 entries (7 days × 3 meals), each with keys: day, meal, dish, calories, protein, carbohydrates, fat, ingredients, steps, image_url, is_fallback. Do not include any additional text or Markdown.
Example:
[{{
  "day": "{base_date.strftime("%a %m-%d")}",
  "meal": "Breakfast",
  "dish": "Spicy Tofu Stir-fry",
  "calories": 350,
  "protein": 20,
  "carbohydrates": 30,
  "fat": 15,
  "ingredients": "Tofu, bell peppers, soy sauce, chili paste",
  "steps": "Stir-fry tofu and peppers with soy sauce and chili.",
  "image_url": "https://images.unsplash.com/photo-1528798834-c90d2b2b2606?ixlib=rb-4.0.3&auto=format&fit=crop&w=280&h=120",
  "is_fallback": false
}}, ...]
"""
    try:
        with st.spinner("Generating your personalized meal plan... 🥗"):
            resp = client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=60
            )
        response_text = resp.choices[0].message.content.strip()
        logging.debug(f"LLM prompt for meal plan: {prompt}")
        logging.debug(f"Raw LLM response for meal plan: {response_text}")
        if not response_text:
            raise ValueError("Empty response from LLM")
        try:
            # Clean response
            response_text = re.sub(r'^```json\n|\n```$', '', response_text).strip()
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            else:
                raise ValueError("No valid JSON array found in response")
            logging.debug(f"Cleaned LLM response: {response_text}")
            
            plan = json.loads(response_text)
            if not isinstance(plan, list) or len(plan) != 21:
                raise ValueError(f"Invalid JSON structure: expected a list with 21 entries, got {len(plan)} entries")
            required_keys = ["day", "meal", "dish", "calories", "protein", "carbohydrates", "fat", "ingredients", "steps", "image_url", "is_fallback"]
            for dish in plan:
                if not all(key in dish for key in required_keys):
                    raise ValueError(f"Missing required JSON fields in dish entry: {set(required_keys) - set(dish.keys())}")
            # Validate image URLs in batch
            urls = [dish["image_url"] for dish in plan]
            valid_urls = batch_validate_urls(urls)
            for dish, is_valid in zip(plan, valid_urls):
                if not is_valid:
                    dish["image_url"] = FALLBACK_IMAGES.get(dish["dish"], FALLBACK_IMAGES[f"Fallback {dish['meal']} Dish"])
            df = pd.DataFrame(plan)
            df["day"] = pd.Categorical(df["day"], categories=[(base_date + timedelta(days=i)).strftime("%a %m-%d") for i in range(7)], ordered=True)
            st.session_state["dish_cache"][cache_key] = df.copy()
            return df
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON format in meal plan response: {e}. Raw response: {response_text}")
            st.error(f"Failed to parse meal plan response: Invalid JSON format ({e}). Using fallback meal plan.")
            return build_recipes_fallback(user, prefs, cuisine, difficulty, exclude, base_date)
    except Exception as e:
        logging.error(f"AI meal plan generation failed: {e}. Raw response: {response_text if 'response_text' in locals() else 'None'}")
        st.error(f"Failed to generate meal plan: {e}. Using fallback meal plan.")
        return build_recipes_fallback(user, prefs, cuisine, difficulty, exclude, base_date)

# Fallback Recipe Generation
def build_recipes_fallback(user, preferences, cuisine, difficulty, exclude_ingredients, base_date: datetime):
    import random
    days = [(base_date + timedelta(days=i)).strftime("%a %m-%d") for i in range(7)]
    recipes = []
    for day in days:
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            available_dishes = []
            for dish in RECIPE_DB[meal].keys():
                dish_data = RECIPE_DB[meal][dish]
                if meets_filter_criteria(dish_data, preferences, cuisine, difficulty, exclude_ingredients):
                    available_dishes.append(dish)
            if not available_dishes:
                new_dish = ai_generate_single_dish(
                    user.get("obesity_level", "Normal_Weight"),
                    user,
                    preferences,
                    cuisine,
                    difficulty,
                    exclude_ingredients,
                    day,
                    meal
                )
                recipes.append(new_dish)
            else:
                dish = random.choice(available_dishes)
                data = RECIPE_DB[meal][dish]
                recipes.append({
                    "day": day, "meal": meal, "dish": dish,
                    "calories": data["calories"], "protein": data["protein"],
                    "carbohydrates": data["carbohydrates"], "fat": data["fat"],
                    "ingredients": data["ingredients"], "steps": data["steps"],
                    "image_url": data["image_url"],
                    "is_fallback": True
                })
    df = pd.DataFrame(recipes)
    df["day"] = pd.Categorical(df["day"], categories=days, ordered=True)
    return df

# Function to check if a dish meets filter criteria
def meets_filter_criteria(dish_data, preferences, cuisine, difficulty, exclude_ingredients):
    include_dish = True
    if any(exclude.lower() in dish_data["ingredients"].lower() for exclude in exclude_ingredients):
        include_dish = False
    if "Vegetarian" in preferences and any(ing.lower() in dish_data["ingredients"].lower() for ing in ["chicken", "cod", "salmon", "tuna", "turkey"]):
        include_dish = False
    if "Gluten-Free" in preferences and any(ing.lower() in dish_data["ingredients"].lower() for ing in ["wheat", "barley", "rye", "bread", "pita"]):
        include_dish = False
    if "High-Protein" in preferences and dish_data["protein"] < 25:
        include_dish = False
    if "Low-Carb" in preferences and dish_data["carbohydrates"] > 40:
        include_dish = False
    if cuisine != "Any" and cuisine.lower() not in dish_data["dish"].lower():
        include_dish = False
    if difficulty != "Any" and difficulty.lower() not in dish_data["steps"].lower():
        include_dish = False
    return include_dish

# Sidebar Inputs
with st.sidebar:
    st.markdown("### 🍎 Dietary Preferences")
    st.markdown(
        "<div class='tip-box'>💡 Tip: To generate the 7-day meal plan faster, please set the filter conditions first (such as dietary preferences, cuisine type, cooking difficulty, and excluded ingredients).</div>",
        unsafe_allow_html=True
    )
    preferences = st.multiselect("Dietary Preferences", ["Vegetarian", "High-Protein", "Low-Carb", "Gluten-Free"])
    cuisine = st.selectbox("Cuisine Type", ["Any", "Asian", "Mediterranean", "American"])
    difficulty = st.selectbox("Cooking Difficulty", ["Any", "Easy", "Medium", "Hard"])
    exclude_ingredients = st.text_input("🚫 Excluded Ingredients (comma-separated)", "").split(",")
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
            if st.button(dish, key=f"favorite_nav_{dish}", on_click=lambda d=dish: st.session_state.update({"selected_dish": d})):
                st.session_state["scroll_to_dish"] = d
        if st.button("🗑️ Clear All Favorites", key="clear_favorites"):
            st.session_state["favorites"] = []
            st.rerun()
    else:
        st.info("No favorite dishes yet. Add some from the meal plan! 🥳")

# User Input Form
with st.form("plan_form"):
    st.markdown("##### 🪪 Personal Information")
    c1, c2 = st.columns(2)
    with c1:
        gender = st.selectbox("⚧️ Gender", ["Male", "Female"])
        age = st.slider("🎂 Age", 0, 120, 30)
        family_history = st.selectbox("🧑‍🧒 Family History of Obesity", ["Yes", "No"])
    with c2:
        height = st.slider("📏 Height (meters)", 0.5, 2.5, 1.7, 0.01)
        weight = st.slider("⚖️ Weight (kg)", 20.0, 200.0, 70.0, 0.1)

    st.markdown("##### 🥕 Diet and Lifestyle")
    c3, c4 = st.columns(2)
    with c3:
        vegetable_days = st.slider("🥬 Vegetable Consumption (days/week)", 0, 7, 3)
        high_calorie_food = st.selectbox("🍿 High-Calorie Food", ["Yes", "No"])
        main_meals = st.slider("🍚 Main Meals per Day", 1, 5, 3)
        snack_frequency = st.selectbox("🍰 Snack Frequency", ["Always", "Frequently", "Occasionally"])
        sugary_drinks = st.selectbox("🥤 Sugary Drinks", ["Yes", "No"])
        water_intake = st.slider("💧 Daily Water Intake (liters)", 0.0, 5.0, 2.0, 0.1)
    with c4:
        alcohol_frequency = st.selectbox("🍷 Alcohol Frequency", ["None", "Occasionally", "Frequently"])
        exercise_days = st.slider("🏋️ Exercise Days per Week", 0, 7, 2)
        screen_time = st.slider("📱 Daily Screen Time (hours)", 0, 24, 3)
        transportation = st.selectbox("🚗 Transportation Mode", ["Car", "Bicycle", "Motorcycle", "Public Transport", "Walking"])
        smoke = st.selectbox("🚬 Smoking", ["Yes", "No"])

    st.markdown("##### 🔛 Plan Start Date")
    base_date = st.date_input("Select Plan Start Date", min_value=datetime.now().date(), value=datetime.now().date())

    submitted = st.form_submit_button("🚀 Generate AI Meal Plan")

# Predict and Generate Meal Plan
if submitted:
    user_inputs = {
        "gender": gender, "age": age, "height": height, "weight": weight,
        "family_history": family_history, "high_calorie_food": high_calorie_food,
        "vegetable_days": vegetable_days, "main_meals": main_meals,
        "snack_frequency": snack_frequency, "smoke": smoke,
        "water_intake": water_intake, "sugary_drinks": sugary_drinks,
        "exercise_days": exercise_days, "screen_time": screen_time,
        "alcohol_frequency": alcohol_frequency, "transportation": transportation,
        "target_calories": 2000, "target_protein": 50,
        "target_carbohydrates": 200, "target_fat": 70
    }
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
                            # Invalidate cache for this specific dish
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