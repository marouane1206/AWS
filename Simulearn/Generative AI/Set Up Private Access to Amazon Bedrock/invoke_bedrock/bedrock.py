import boto3
import json
from datetime import datetime
import os

model_id = os.environ.get('BEDROCK_MODEL_ID')

def test_bedrock():
    model_id = os.environ.get('BEDROCK_MODEL_ID')
    prompt_data = "What is the envelope budget method?"
    r = call_bedrock(model_id, prompt_data)
    
    return("""
    \n\n\n
    Model latency: %s\n
    Response:\n
    %s
    \n\n\n
    """ % (r['latency'],r['response'])
    )
    
def call_bedrock(model_id, prompt_data):
    bedrock_runtime = boto3.client('bedrock-runtime')

    body = json.dumps({
        "inputText": prompt_data,
        "textGenerationConfig":
        {
            "maxTokenCount":1000,
            "stopSequences":[],
            "temperature":0.7,
            "topP":0.9
        }
    })
    accept = 'application/json'
    content_type = 'application/json'

    before = datetime.now()
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id, accept=accept, contentType=content_type)
    latency = (datetime.now() - before).seconds
    response_body = json.loads(response.get('body').read())
    response = response_body.get('results')[0].get('outputText')

    return {
        'latency': str(latency),
        'response': response
    }
    
def json_to_pretty_table(json_data):
    data = json.loads(json_data)
    table = PrettyTable()
    
    # Assuming all rows have the same keys
    headers = data['rows'][0].keys()
    table.field_names = headers
    
    for row in data['rows']:
        table.add_row(row.values())
    
    return table
    
def generate_budget_report(customer_data):
    
    prompt_data = f"""
        Using the spending data in the table bellow, aggregate the spending by category and provide the total for each category.

        Customer Spending Table:
        
        %s
    
    """ % (customer_data)
    
    
    r = call_bedrock(model_id,prompt_data)
    return r['response']

