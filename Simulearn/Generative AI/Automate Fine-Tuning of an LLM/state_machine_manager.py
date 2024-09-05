import boto3
import datetime
import random
import uuid
import logging
import stepfunctions
import sagemaker
import io
import random
import json
import sys
from sagemaker import djl_inference

from sagemaker import image_uris
from sagemaker import Model
from stepfunctions import steps
from stepfunctions.steps import *
from stepfunctions.workflow import Workflow

iam = boto3.client('iam')
s3 = boto3.client('s3')

stepfunctions.set_stream_logger(level=logging.INFO)

### SET UP STEP FUNCTIONS ###
unique_timestamp = f"{datetime.datetime.now():%H-%m-%S}"
state_machine_name = f'FineTuningLLM-{unique_timestamp}'
notebook_name = f'fine-tuning-llm-{unique_timestamp}'
succeed_state = Succeed("HelloWorldSuccessful")
fail_state = Fail("HelloWorldFailed")
new_model_name = f"trained-dolly-{unique_timestamp}"

try:
    # Get a list of all bucket names
    bucket_list = s3.list_buckets()

    # Filter bucket names starting with 'automate'
    bucket_names = [bucket['Name'] for bucket in bucket_list['Buckets'] if bucket['Name'].startswith('automate')]
    mybucket = bucket_names[0].strip("'[]")
except Exception as e:
    print(f"Error: {e}")



# Get the stepfunction_workflow_role
try:
    role = iam.get_role(RoleName='stepfunction_workflow_role')
    workflow_role = role['Role']['Arn']
except iam.exceptions.NoSuchEntityException:
    print("The role 'stepfunction_workflow_role' does not exist.")

# Get the sagemaker_exec_role
try:
    role2 = iam.get_role(RoleName='sagemaker_exec_role')
    sagemaker_exec_role = role2['Role']['Arn']
except iam.exceptions.NoSuchEntityException:
    print("The role 'sagemaker_exec_role' does not exist.")

# Create a SageMaker model object
model_data="s3://{}/output/lora_model.tar.gz".format(mybucket)

image_uri = image_uris.retrieve(framework="djl-deepspeed",
                                version="0.22.1",
                                region="us-east-1")
trained_dolly_model = Model(image_uri=image_uri,
              model_data=model_data,
              predictor_cls=djl_inference.DJLPredictor,
              role=sagemaker_exec_role)

# Create a retry configuration for SageMaker throttling exceptions. This is attached to
# the SageMaker steps to ensure they are retried until they run.
SageMaker_throttling_retry = stepfunctions.steps.states.Retry(
    error_equals=['ThrottlingException', 'SageMaker.AmazonSageMakerException'],
    interval_seconds=5,
    max_attempts=60,
    backoff_rate=1.25
)
# Create a state machinestep to create the model
model_step = steps.ModelStep(
    'Create model',
    model=trained_dolly_model,
    model_name=new_model_name
)
# Add a retry configuration to the model_step
model_step.add_retry(SageMaker_throttling_retry)

# Create notebook for running SageMaker training job.
create_sagemaker_notebook = LambdaStep(
    state_id="Create training job",
    parameters={
        "FunctionName": "create_notebook_function",
        "Payload": {"notebook_name": notebook_name},        
    },
)
# Get notebook status
get_notebook_status = LambdaStep(
    state_id="Get training job status",
    parameters={
        "FunctionName": "get_notebook_status_function",
        "Payload": {"notebook_name": notebook_name},          
    },
)

#choice state
response_notebook_status = Choice(state_id="Response to training job status")
wait_for_training_job = Wait(
    state_id="Wait for training job",
    seconds=150)
wait_for_training_job.next(get_notebook_status)
#retry checking notebook status
response_notebook_status.add_choice(
    rule=ChoiceRule.StringEquals(
        variable="$.Payload.trainningstatus", value="Failed"
    ),
    next_step=fail_state,
)
response_notebook_status.add_choice(
    rule=ChoiceRule.StringEquals(
        variable="$.Payload.trainningstatus", value="Stopped"
    ),
    next_step=fail_state,
)
response_notebook_status.add_choice(
    ChoiceRule.StringEquals(
        variable="$.Payload.trainningstatus", value="NotAvailable"
    ),
    next_step=fail_state,
)
inservice_rule=ChoiceRule.StringEquals(
        variable="$.Payload.trainningstatus", value="InService"
    )
response_notebook_status.add_choice(
    ChoiceRule.Not(inservice_rule),
    next_step=wait_for_training_job,
)

# Create a step to generate an Amazon SageMaker endpoint configuration
endpoint_config_step = steps.EndpointConfigStep(
    "Create endpoint configuration",
    endpoint_config_name=new_model_name,
    model_name=new_model_name,
    initial_instance_count=1,
    instance_type='ml.g4dn.2xlarge'
)
# Add a retry configuration to the endpoint_config_step
endpoint_config_step.add_retry(SageMaker_throttling_retry)

# Create a step to generate an Amazon SageMaker endpoint
endpoint_step = steps.EndpointStep(
    "Create endpoint",
    endpoint_name=f"endpoint-{new_model_name}",
    endpoint_config_name=new_model_name
    )
# Add a retry configuration to the endpoint_step
endpoint_step.add_retry(SageMaker_throttling_retry)

# Chain the steps together to generate a full AWS Step Function
workflow_definition = steps.Chain([
    create_sagemaker_notebook,
    wait_for_training_job,
    get_notebook_status,
    response_notebook_status,
    model_step,
    endpoint_config_step,
    endpoint_step
])

# Create an AWS Step Functions workflow based on inputs
basic_workflow = Workflow(
    name=state_machine_name,
    definition=workflow_definition,
    role=workflow_role,
)

jsonDef = basic_workflow.definition.to_json(pretty=True)

print('---------')
print(jsonDef)
print('---------')

basic_workflow.create()