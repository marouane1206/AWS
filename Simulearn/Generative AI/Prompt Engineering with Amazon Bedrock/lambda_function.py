#!/usr/bin/env python3
import boto3
import json
from datetime import datetime


def lambda_handler(event, context):
    print(event, context)

    body = event['body'] 
    path = event['path']
    method = event['httpMethod']
    prompt = json.loads(body)['prompt']

    if path == "/invokemodel" and method == "POST":
        model_id = 'amazon.titan-text-premier-v1:0'
        model_response = call_bedrock(model_id, prompt)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(model_response)
        }
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Not Found'})
        }


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
    print("bedrock-input:", body)

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
