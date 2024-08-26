import boto3
import json

import json
import os
import sys

module_path = ".."
sys.path.append(os.path.abspath(module_path))

region_name = 'us-east-1'
bedrock = boto3.client(service_name='bedrock', region_name=os.environ.get("AWS_DEFAULT_REGION", None))
model_list=bedrock.list_foundation_models()
for x in range(len(model_list.get('modelSummaries'))):
     print(model_list.get('modelSummaries')[x]['modelId'])


bedrock_rt = boto3.client(service_name='bedrock-runtime', region_name=region_name)
prompt = "What is Amazon Bedrock?"
configs= {
"inputText": prompt,
"textGenerationConfig": {
"maxTokenCount": 4096,
"stopSequences": [],
"temperature":0,
"topP":1
}
}
body=json.dumps(configs)
modelId = 'amazon.titan-tg1-large'
accept = 'application/json'
contentType = 'application/json'
response = bedrock_rt.invoke_model(
     body=body,
     modelId=modelId,
     accept=accept,
     contentType=contentType
)
response_body = json.loads(response.get('body').read())
print(response_body.get('results')[0].get('outputText'))