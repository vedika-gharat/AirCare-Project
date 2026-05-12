import streamlit as st
import requests
import smtplib
from email.message import EmailMessage
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

# 1. AQI Fetch
def get_aqi(city):
    token = "c7e3deca183710c1852ed747a39514912118a18f"  # 🔑 Replace with your WAQI token
    url = f"https://api.waqi.info/feed/{city}/?token={token}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data["status"] == "ok":
            return data["data"]["aqi"]
        else:
            return fallback_aqi(city)
    except:
        return fallback_aqi(city)

def fallback_aqi(city):
    defaults = {"Delhi": 180, "Mumbai": 90, "Kolkata": 160, "Bangalore": 80, "Hyderabad": 120}
    return defaults.get(city.strip().title(), None)

# 2. ML Model
def train_model():
    df = pd.DataFrame({
        'aqi': [50, 120, 180, 250, 90, 135],
        'age': [25, 60, 40, 70, 30, 50],
        'asthma': [0, 1, 0, 1, 0, 1],
        'heart': [0, 0, 1, 1, 0, 1],
        'allergies': [0, 1, 0, 1, 0, 1],
        'pregnant': [0, 0, 0, 1, 0, 1],
        'activity': [0, 2, 1, 2, 0, 1],
        'risk': ['Low', 'High', 'Medium', 'High', 'Low', 'High']
    })
    X = df.drop('risk', axis=1)
    y = df['risk']
    model = DecisionTreeClassifier()
    model.fit(X, y)
    return model

model = train_model()

# 3. Email Alert
def send_email(to_email, risk, city, aqi):
    sender_email = "vedikagharat555@gmail.com"               # ✉️ Replace with your Gmail
    app_password = "saqo oghn hvrr phll"             # 🔐 Replace with your Gmail App Password
    receiver_email = st.text_input("vedikagharat0@gmail.com")

    subject = f"AirCare Alert: {risk} Air Quality in {city}"
    body = f"""Hello,

This is an automated alert from AirCare.

The current AQI in {city} is {aqi}, which is considered a {risk} health risk.

Please take precautions:
- Avoid outdoor activity
- Wear a mask
- Stay hydrated

Stay safe,
AirCare Team
"""

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print("✅ Email sent to:", to_email)
    except Exception as e:
        print("❌ Email sending failed:", e)

# 4. Streamlit UI
st.set_page_config(page_title="AirCare", layout="centered")
st.title("🌍 AirCare: AI-Based Air Quality & Health Alert Assistant")

city = st.text_input("📍 Enter your city:")
age = st.slider("🎂 Your Age", 1, 100, 25)
asthma = st.checkbox("💨 Asthma")
heart = st.checkbox("❤️ Heart condition")
allergies = st.checkbox("🤧 Allergies")
pregnant = st.checkbox("🤰 Pregnant")
activity_level = st.radio("🏃 Outdoor Activity Level", ["Low", "Medium", "High"])
receiver_email = st.text_input("📧 Enter your email to receive alerts:")

# Convert to numeric
asthma_val = int(asthma)
heart_val = int(heart)
allergies_val = int(allergies)
pregnant_val = int(pregnant)
activity_val = {"Low": 0, "Medium": 1, "High": 2}[activity_level]

# Check Button
if st.button("🔍 Check AQI & Risk"):
    aqi = get_aqi(city)
    if aqi is not None:
        st.success(f"AQI in {city}: {aqi}")
        risk = model.predict([[aqi, age, asthma_val, heart_val, allergies_val, pregnant_val, activity_val]])[0]
        st.subheader(f"🩺 Health Risk: {risk}")
        
        if risk == "High":
            st.error("⚠️ High Risk! Avoid going out.")
        elif risk == "Medium":
            st.warning("😷 Medium Risk. Be cautious outside.")
        else:
            st.info("✅ Low Risk. You're safe.")

        # Send Email Automatically
        if risk != "Low" and receiver_email:
            send_email(receiver_email, risk, city, aqi)
            st.success(f"📧 Alert sent to {receiver_email}")
    else:
        st.error("❌ Couldn't fetch AQI. Please check the city name.")
