import streamlit as st
import requests

# Define the Flask API URL
FLASK_API_URL = "http://127.0.0.1:5000/recommendations"  # Update with your Flask API URL if different

# Streamlit interface
st.title("Mutual Funds Recommendation System")

with st.form(key="user_info_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=18, max_value=100, step=1)
    income = st.number_input("Income", min_value=0, step=1000)
    expenses = st.number_input("Expenses", min_value=0, step=100)
    debt = st.number_input("Debt", min_value=0, step=100)
    savings = st.number_input("Savings", min_value=0, step=100)
    risk_preference = st.selectbox("Risk Preference", ["Low", "Medium", "High"])
    submit_button = st.form_submit_button(label="Get Recommendations")

if submit_button:
    payload = {
        "name": name,
        "age": age,
        "income": income,
        "expenses": expenses,
        "debt": debt,
        "savings": savings,
        "risk_preference": risk_preference,
    }

    response = requests.post(FLASK_API_URL, json=payload)
    recommendations = response.json().get(
        "recommendations", "No recommendations found."
    )

    st.subheader("Recommendations")
    st.write(recommendations)
