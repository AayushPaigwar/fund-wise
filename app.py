import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import openai
from langchain_community.llms import AzureOpenAI
from langchain_community.chat_models import AzureChatOpenAI

# Load environment variables from .env file
load_dotenv()

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
    deployment_name="gpt-35-turbo",  # Your Azure deployment name
    temperature=0.7,
)


def get_recommendations(name, age, income, expenses, debt, savings, risk_preference):
    prompt = f"""
User: {name}, {age}, Income: {income}, Expenses: {expenses}, Debt: {debt}, Savings: {savings}, Risk: {risk_preference}
Recommend 3 mutual funds. For each, give:
1. Fund name

2. Risk level

3. Expected returns

4. Description

Format:
1. Fund: ...

   Risk: ...
   
   Returns: ...
   
   Description: ...

2. Fund: ...

   Risk: ...
   
   Returns: ...
   
   Description: ...

3. Fund: ...

   Risk: ...
   
   Returns: ...
   
   Description: ...
"""

    try:
        response = llm(prompt)
        return response
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/")
def home():
    return "Mutual Funds Recommendation System Backend API"


@app.route("/recommendations", methods=["POST"])
def recommendations():
    data = request.json
    name = data["name"]
    age = data["age"]
    income = data["income"]
    expenses = data["expenses"]
    debt = data["debt"]
    savings = data["savings"]
    risk_preference = data["risk_preference"]

    recommendations = get_recommendations(
        name, age, income, expenses, debt, savings, risk_preference
    )
    return jsonify({"recommendations": recommendations})


if __name__ == "__main__":
    app.run(debug=False)


# -=============================================================================

# from flask import Flask, request, jsonify
# import pandas as pd
# import openai
# from langchain_community.llms import AzureOpenAI

# app = Flask(__name__)

# # Azure OpenAI configuration
# OPENAI_API_KEY = "884039b2dd764c80a0297dfd9f57f6e2"
# OPENAI_API_TYPE = "Azure"
# AZURE_ENDPOINT = "https://demo-model.openai.azure.com/"
# OPENAI_API_VERSION = "2024-02-01"


# # Initialize OpenAI API
# openai.api_type = OPENAI_API_TYPE
# openai.api_version = OPENAI_API_VERSION
# openai.api_key = OPENAI_API_KEY


# # Initialize Azure OpenAI LLM
# llm = AzureOpenAI(
#     openai_api_version=OPENAI_API_VERSION,
#     openai_api_key=OPENAI_API_KEY,
#     azure_endpoint=AZURE_ENDPOINT,
#     openai_api_type=OPENAI_API_TYPE,
#     deployment_name="gpt-35-turbo",
#     temperature=0.7,  # temperature: 0.1 = more conservative, 0.9 = more creative
# )

# # Load CSV data into a DataFrame
# df = pd.read_csv("MF_India_AI.csv")

# # print("Column names in DataFrame:", df.columns)
# print(df[["amc_name", "risk_level", "returns_1yr", "returns_3yr", "returns_5yr"]])


# def get_recommendations(name, age, income, expenses, debt, savings, risk_preference):
#     # Filter data based on risk preference
#     risk_level_mapping = {"Low": 1, "Medium": 3, "High": 6}
#     risk_level = risk_level_mapping.get(risk_preference, 1)

#     filtered_df = df["risk_level"] <= risk_level

#     # Sort by returns (you can customize this based on your preference)
#     filtered_df["average_returns"] = filtered_df[
#         ["returns_1yr", "returns_3yr", "returns_5yr"]
#     ].apply(
#         lambda x: (
#             float(x[0].strip("%")) + float(x[1].strip("%")) + float(x[2].strip("%"))
#         )
#         / 3,
#         axis=1,
#     )

#     filtered_df = filtered_df.sort_values(by="average_returns", ascending=False)

#     # Generate recommendations (taking top 3 for simplicity)
#     recommendations = filtered_df.head(3)

#     # Prepare response in the desired format
#     recommendations_list = recommendations[
#         [
#             "amc_name",
#             "risk_level",
#             "returns_1yr",
#             "returns_3yr",
#             "returns_5y",
#             "category",
#         ]
#     ].to_dict(orient="records")
#     return recommendations_list


# # Routes for the Flask API


# # home route: /
# @app.route("/")
# def home():
#     return "Mutual Funds Recommendation System Backend API"


# # route: /recommendations
# @app.route("/recommendations", methods=["POST"])
# def recommendations():
#     data = request.json
#     name = data["name"]
#     age = data["age"]
#     income = data["income"]
#     expenses = data["expenses"]
#     debt = data["debt"]
#     savings = data["savings"]
#     risk_preference = data["risk_preference"]

#     recommendations = get_recommendations(
#         name, age, income, expenses, debt, savings, risk_preference
#     )
#     return jsonify({"recommendations": recommendations})


# if __name__ == "__main__":
#     app.run(debug=False)
