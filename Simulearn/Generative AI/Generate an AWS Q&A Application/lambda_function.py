# Import necessary libraries
import json
import boto3
import os
import re
import logging

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from template import sagemaker_faqs_template, bedrock_faqs_template, bedrock_rag_faqs_template


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Create a Bedrock Runtime client
bedrock_client = boto3.client('bedrock-runtime')


# Define Lambda function
def lambda_handler(event, context):
    # Log the incoming event in JSON format
    logger.info('Event: %s', json.dumps(event))

    request_body = json.loads(event['body'])
    content  = request_body.get('content')
        
    # Generate the prompt
    template_function_name = os.environ['TEMPLATE_FUNCTION']
    template_generator = eval(template_function_name)

    template = template_generator(context=content)
    
    prompt_template = ChatPromptTemplate(
        messages=[HumanMessagePromptTemplate.from_template(template)],
        input_variables=["context"],
    )
    
    prompt = prompt_template.format(context=content)
    
    # Prepare the input data for the model
    input_data = {
        "inputText": prompt,
        "textGenerationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "maxTokenCount": 2048,
            "stopSequences": []
        }
    }
    
    # Log the input data
    logger.info('Input data: %s', json.dumps(input_data))

    # Invoke the Bedrock Runtime with the cleaned body as payload
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-text-premier-v1:0",
        body=json.dumps(input_data).encode("utf-8"),
        accept='application/json',
        contentType='application/json'
    )

    # Load the response body and decode it
    result = json.loads(response["body"].read().decode())
    
    # Log the response payload
    logger.info('Response payload: %s', json.dumps(result))
    
    # Extract the generated text from the response
    generated_text = ""
    if "results" in result and result["results"]:
        generated_text = result["results"][0].get("outputText", "").replace("\\n", "\n")

    # Parse the generated text and extract questions, options, and correct answers
    quiz = []
    questions = re.split(r'\n\nQ\d+:', generated_text)
    
    for question_text in questions[1:]:
        question_text = question_text.strip()
        
        if not question_text:
            continue

        # Extract the question
        question = re.search(r'^(.*?)\n', question_text).group(1)
        
        # Extract the options
        options = re.findall(r'[a-d]\. (.*?)(?=\n[a-d]\.|$|(?=\n\n))', question_text)

        # Extract the correct answer index
        correct_answer_match = re.search(r'Correct Answer: ([a-d])\.', question_text)
        if correct_answer_match:
            correct_answer_index = ord(correct_answer_match.group(1).lower()) - ord('a')
        else:
            correct_answer_index = None

        quiz.append({
            'question': question,
            'options': options,
            'correct_answer_index': correct_answer_index
        })

    # Return the quiz as JSON
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps({'quiz': quiz})
    }