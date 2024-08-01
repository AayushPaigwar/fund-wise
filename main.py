import streamlit as st
import requests

# Set up Streamlit UI
st.title("Mutual Fund Recommendation System")

# User input fields
name = st.text_input("Name")
age = st.number_input("Age", min_value=0)
income = st.number_input("Income", min_value=0)
expenses = st.number_input("Expenses", min_value=0)
debt = st.number_input("Debt", min_value=0)
savings = st.number_input("Savings", min_value=0)
risk = st.selectbox("Risk Preference", ["Low", "Medium", "High"])

# Button to get recommendation
if st.button("Get Recommendation"):
    # Format user input
    user_input = f"User: {name}, {age}, Income: {income}, Expenses: {expenses}, Debt: {debt}, Savings: {savings}, Risk: {risk}"

    # Send request to Flask backend
    response = requests.post(
        "http://localhost:5000/recommend", json={"user_input": user_input}
    )

    # Check for response
    if response.status_code == 200:
        recommendation = response.json()

        # Display mutual fund recommendations
        st.write("### Recommendation")
        st.write(f"**Asset Allocation:**")
        st.write(f"Debt: {recommendation['debt_allocation']}")
        st.write(f"Hybrid: {recommendation['hybrid_allocation']}")
        st.write(f"Equity: {recommendation['equity_allocation']}")

        st.write("### Recommendation")
        st.write(f"**Fund Name:** {recommendation['fund_name']}")
        st.write(f"**Risk Level:** {recommendation['risk_level']}")
        st.write(f"**Expected Returns:** {recommendation['expected_returns']}")
        st.write(f"**Description:** {recommendation['description']}")

    else:
        st.error("Failed to get recommendation. Please try again.")
