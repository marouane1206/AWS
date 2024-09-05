import json
import boto3
import streamlit as st

# Set the page title
st.set_page_config(page_title="Streamlit App")

# Add a title
st.title("Code Analysis App by Streamlit!")

# create a sidebar
with st.sidebar:
    # Add a drop down list to select the LLM models
    models = ["Amazon Titan", "Mistral AI"]
    model = st.selectbox("Choose a model", models)

    # map values to LLM models
    if model == "Amazon Titan":
        model_id = "amazon.titan-text-premier-v1:0"
    else:
        model_id = "mistral.mistral-7b-instruct-v0:2"

    # Add a slider for temperature
    temperature = st.slider("Choose Temperature:", 0.0, 1.0, 0.5)
    temperature = temperature

    # Add a slider for max tokens
    max_tokens = st.slider("Choose Max tokens:", 0, 1024, 20)
    max_tokens = max_tokens

    # Add a slider for top p
    top_p = st.slider("Choose Top_p:", 0.0, 1.0, 0.5)
    top_p = top_p

st.divider()

# Add a paragraph to enter the prompt
src_cde = st.text_area("Enter source code here", height=200)
code_analysis = st.text_area("Enter code analysis finding here")
request = st.text_area("Enter request here")

prompt = "Source Code: " + src_cde + " " + "Code Analysis Finding: " + code_analysis + " " + "Request: " + request 


# Construct a json object with the params and prompt
input_payload = {
    "query": prompt,
    "model_id": model_id,
    "temperature": temperature,
    "max_tokens": max_tokens,
    "top_p": top_p,
}

lambda_client = boto3.client("lambda")


#  Function to invoke the Lambda function
def invoke_lambda():
    response = lambda_client.invoke(
        FunctionName="bedrock_function", Payload=json.dumps({"body": input_payload})
    )

    result = response["Payload"].read().decode("utf-8")
    json_result = json.loads(result)
    st.markdown(json_result)


# Add a button
if st.button("Run"):
    invoke_lambda()