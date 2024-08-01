from flask import Flask, request, jsonify
import openai
from langchain_openai import AzureOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import streamlit as st
import pandas as pd
import requests
import threading

# environment variables with env
from dotenv import load_dotenv

import os

load_dotenv()
# Flask app setup
app = Flask(__name__)

# Azure OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

openai.api_type = OPENAI_API_TYPE
openai.api_version = OPENAI_API_VERSION
openai.api_key = OPENAI_API_KEY

llm = AzureOpenAI(
    openai_api_version=OPENAI_API_VERSION,
    openai_api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    openai_api_type=OPENAI_API_TYPE,
    deployment_name="gpt-35-turbo",
    temperature=0.2,
)


class MutualFundRecommendation(BaseModel):
    debt_allocation: str = Field(
        description="debt allocation of the mutual fund according to the users input in percentage also give the number of amount in INR"
    )
    hybrid_allocation: str = Field(
        description="hybrid allocation of the mutual fund  according to the users input in percentage also give the number of amount in INR"
    )
    equity_allocation: str = Field(
        description="equity allocation of the mutual fund  according to the users input in percentag also give the number of amount in INR"
    )
    fund_name: str = Field(description="name of the mutual fund")
    risk_level: str = Field(description="risk level of the mutual fund")
    expected_returns: str = Field(description="expected returns of the mutual fund")
    description: str = Field(description="short description of the mutual fund")


parser = JsonOutputParser(pydantic_object=MutualFundRecommendation)
format_response_parser = parser.get_format_instructions()

custom_prompt = """
Answer the Query. \n
{format_instructions} \n
Question: {question}
"""

prompt = PromptTemplate(
    template=custom_prompt,
    input_variables=["question"],
    partial_variables={"format_instructions": format_response_parser},
)

chain = prompt | llm | parser


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user_input = data.get("user_input", "")
    response = chain.invoke(input=user_input)
    return jsonify(response)


def run_flask():
    app.run(debug=False, use_reloader=False)


# Start Flask app in a separate thread
thread = threading.Thread(target=run_flask)
thread.start()

# Streamlit app setup
st.title("Asset Allocation Report Generator")

age = st.number_input("Enter your age:", min_value=1, max_value=100, value=21)
annual_salary = st.number_input(
    "Enter your annual salary (₹):", min_value=0, value=1000000
)
monthly_expenses = st.number_input(
    "Enter your monthly expenses (₹):", min_value=0, value=50000
)
monthly_loan = st.number_input(
    "Enter your monthly loan repayment (₹):", min_value=0, value=10000
)
monthly_emergency_fund = st.number_input(
    "Enter your monthly emergency fund contribution (₹):", min_value=0, value=10000
)


def get_asset_allocation_report(
    age, annual_salary, monthly_expenses, monthly_loan, monthly_emergency_fund
):
    prompt = f"""
    User Details:
    Age: {age}
    Annual Salary: ₹{annual_salary}
    Monthly Expenses: ₹{monthly_expenses}
    Monthly Loan Repayment: ₹{monthly_loan}
    Monthly Emergency Fund Contribution: ₹{monthly_emergency_fund}

    Calculate the monthly salary, monthly savings, determine the risk factor, and provide a recommended asset allocation strategy with the following breakdown:
    - Equity (High Risk)
    - Hybrid (Moderate Risk)
    - Debt (Low Risk)

    Provide the recommended allocation percentages and the exact investment amounts based on the monthly savings. Summarize the risk factor and the investment breakdown.
    
    Generate a report in the following template:
    1. Calculate Disposable Income:
    Annual Salary: ₹{annual_salary}
    Monthly Salary: 
    Monthly Expenses: ₹{monthly_expenses}
    Monthly Loan Repayment: ₹{monthly_loan}
    Monthly Emergency Fund Contribution: ₹{monthly_emergency_fund}
    Monthly Savings: 

    2. Risk Factor Determination:
    Age: {age}
    Risk Factor: 

    3. Asset Allocation Strategy:
    Equity (High Risk): 
    Hybrid (Moderate Risk): 
    Debt (Low Risk): 

    4. Recommended Allocation:
    Given your age and financial position, a higher allocation to equity is advisable.

    5. Investment Calculation:
    Let's allocate your monthly savings of ₹ into these categories:
    Equity: ₹
    Hybrid: ₹
    Debt: ₹

    6. Summary:
    Equity: % (₹ per month)
    Hybrid: % (₹ per month)
    Debt: % (₹ per month)
    Risk Factor: 
    """

    try:
        response = requests.post(
            "http://127.0.0.1:5000/recommend", json={"user_input": prompt}
        )
        return response.json()
    except Exception as e:
        st.error(f"An error occurred while generating the report: {e}")
        return None


def parse_report(raw_output):
    parsed_output = {}
    sections = raw_output.split("\n\n")

    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].strip()
        content = "\n".join(lines[1:]).strip()
        parsed_output[title] = content

    return parsed_output


def extract_allocation_details(parsed_output):
    allocation = {"Equity": 0, "Hybrid": 0, "Debt": 0}
    for key, value in parsed_output.items():
        if key.startswith("Asset Allocation Strategy"):
            lines = value.split("\n")
            for line in lines:
                if "Equity" in line:
                    allocation["Equity"] = float(
                        line.split(":")[1].strip().replace("%", "")
                    )
                elif "Hybrid" in line:
                    allocation["Hybrid"] = float(
                        line.split(":")[1].strip().replace("%", "")
                    )
                elif "Debt" in line:
                    allocation["Debt"] = float(
                        line.split(":")[1].strip().replace("%", "")
                    )
    return allocation


def recommend_funds(funds_data, allocation, monthly_savings):
    recommended_funds = {}
    for category in allocation:
        percentage = allocation[category]
        amount = (percentage / 100) * monthly_savings
        funds = funds_data[funds_data["Category"] == category].nlargest(
            3, "Returns"
        )  # Top 3 funds based on Returns
        recommended_funds[category] = {"amount": amount, "funds": funds}
    return recommended_funds


def display_recommended_funds(recommended_funds):
    for category, details in recommended_funds.items():
        st.subheader(f"{category} Funds")
        st.write(f'Allocated Amount: ₹{details["amount"]:.2f}')
        st.table(details["funds"])


# Load the mutual fund data
funds_data = pd.read_csv("./MF_India_AI.csv")

if st.button("Generate Report"):
    raw_report = get_asset_allocation_report(
        age=age,
        annual_salary=annual_salary,
        monthly_expenses=monthly_expenses,
        monthly_loan=monthly_loan,
        monthly_emergency_fund=monthly_emergency_fund,
    )

    if raw_report:
        parsed_report = parse_report(raw_report)
        st.subheader("Generated Report")
        for title, content in parsed_report.items():
            st.subheader(title)
            st.write(content)

        # Extracting monthly savings from the parsed report
        monthly_savings_line = [
            line
            for line in parsed_report["1. Calculate Disposable Income:"].split("\n")
            if "Monthly Savings" in line
        ][0]
        monthly_savings = float(
            monthly_savings_line.split(":")[1].strip().replace("₹", "").replace(",", "")
        )

        # Extracting allocation details
        allocation = extract_allocation_details(parsed_report)

        # Recommending funds based on the allocation and savings
        recommended_funds = recommend_funds(funds_data, allocation, monthly_savings)
        display_recommended_funds(recommended_funds)
