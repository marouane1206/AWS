import streamlit as st
import boto3
import json
import os

# Set the page title
st.set_page_config(page_title="Streamlit App")

# Add a title
st.title("Welcome to Streamlit App!")

# Add some text
st.write("This is a simple Streamlit application that invokes a Lambda function.")

# Add a text input
name = st.text_input("Enter your prompt here....")

lambda_client = boto3.client("lambda")

#  Function to invoke the Lambda function
def invoke_lambda():
    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(
        FunctionName="guard_chat_function",
        Payload=json.dumps({"prompt": name})
    )
    result = json.load(response["Payload"])
    st.write(result)
    


# Add a button
if st.button("Submit prompt"):
    invoke_lambda()







