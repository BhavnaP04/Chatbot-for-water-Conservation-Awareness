# streamlit_app.py

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Page Setup ---
st.set_page_config(page_title="AquaAdvisor 💧", layout="centered")
st.title("💧 AquaAdvisor – Your AI Water & Sanitation Guide")
st.markdown("Use this app to estimate your water footprint and get personalized water-saving tips.")

# --- Load API Key ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 GEMINI_API_KEY not found. Please set it correctly in your .env file.")
    st.stop()
else:
    genai.configure(api_key=api_key)

# --- Initialize Gemini Model ---
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"❌ Error initializing Gemini model: {e}")
    st.stop()

# --- Water Footprint Constants ---
WATER_FOOTPRINT_FACTORS = {
    "shower_per_min": 9,
    "toilet_flush": 6,
    "laundry_load": 75,
    "bottled_water_prod": 3,
}

# --- Sidebar Inputs ---
st.sidebar.header("🧾 Input Your Details")

shower_min = st.sidebar.number_input("🚿 Daily Shower Time (in minutes)", min_value=0, value=10)
toilet_flushes = st.sidebar.number_input("🚽 Daily Toilet Flushes", min_value=0, value=5)
laundry_loads = st.sidebar.number_input("🧺 Weekly Laundry Loads", min_value=0, value=3)
bottled_water = st.sidebar.number_input("💧 Weekly Bottled Water Consumption (Liters)", min_value=0.0, value=2.0)

if st.sidebar.button("Calculate Water Footprint"):
    # --- Water Usage Calculation ---
    shower_usage = shower_min * WATER_FOOTPRINT_FACTORS["shower_per_min"]
    flush_usage = toilet_flushes * WATER_FOOTPRINT_FACTORS["toilet_flush"]
    laundry_usage_daily = (laundry_loads * WATER_FOOTPRINT_FACTORS["laundry_load"]) / 7
    bottled_water_virtual = (bottled_water * WATER_FOOTPRINT_FACTORS["bottled_water_prod"]) / 7

    total_daily_footprint = round(shower_usage + flush_usage + laundry_usage_daily + bottled_water_virtual, 1)

    st.subheader("📊 Estimated Daily Water Footprint")
    st.metric("💧 Liters per Day", f"{total_daily_footprint} L")
    st.info("💡 For context, the global average is ~130 liters/person/day for household use.")

    # --- Gemini Prompt ---
    prompt = f"""
    You are an AI Water Conservation and Sanitation Specialist named AquaAdvisor.
    Your goal is to provide actionable, encouraging, and personalized advice based on a user's water consumption data.
    The user wants to reduce their water footprint and learn about sanitation.

    User's Data:
    - Daily Shower Time: {shower_min} minutes
    - Daily Toilet Flushes: {toilet_flushes}
    - Weekly Laundry Loads: {laundry_loads}
    - Weekly Bottled Water Consumption: {bottled_water} Liters
    - Calculated Daily Water Footprint: {total_daily_footprint} Liters

    Based on this data, provide 3 distinct and practical tips. For each tip:
    1. Directly address one of the user's highest consumption areas.
    2. Explain the potential water savings in simple terms.
    3. Conclude with a general, encouraging tip about the importance of clean water access or simple sanitation practices (like proper handwashing or not pouring fats down the drain).

    Keep the tone friendly and helpful. Use emojis and markdown formatting where appropriate.
    """

    st.subheader("⏳ Generating Your Personalized Tips...")

    try:
        response = model.generate_content(prompt)
        st.markdown("### ✨ Your Personalized Action Plan ✨")
        st.markdown(response.text.strip())
    except Exception as e:
        st.error(f"❌ Error generating response: {e}")
