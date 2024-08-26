"""
The code is developed using reference from
https://docs.aws.amazon.com/transcribe/latest/dg/getting-started-python.html
"""

import json
import logging
import boto3
import datetime
from urllib.parse import unquote_plus

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Boto3 - s3 Client
# You will use the client to upload files to S3 bucket
# More Info: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-creating-buckets.html
s3 = boto3.client('s3')

# Declare output file path and name
output_key = "output/transcribe_response.json"


def lambda_handler(event, context):
    """
    This code gets the S3 attributes from the trigger event,
    then invokes the transcribe api to analyze audio files asynchronously.
    """

    # log the event
    logger.info(event)
    # Iterate through the event
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])

        # Using Amazon Transcribe client
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/transcribe.html
        transcribe = boto3.client('transcribe')
        
        # Using datetime to create a unique job name.
        now = datetime.datetime.now()
        job_uri = f's3://{bucket}/{key}'
        job_name = f'transcribe_job_{now:%Y-%m-%d-%H-%M}'

        # Transcribe audio file
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/transcribe.html#TranscribeService.Client.start_transcription_job
        try:
            response = transcribe.start_transcription_job(      # You are using start_transcription_job asynchronous API
                            TranscriptionJobName=job_name,
                            Media={'MediaFileUri': job_uri},
                            MediaFormat='<Enter_Your_Media_Format>', # There are several media formats supported.
                            LanguageCode='en-US',                    # The language code for the language used in the input media file.
                            OutputBucketName=bucket,
                            OutputKey=f'output/{job_name}.json',
                        )
            

            logger.info(response)
            return_result = {"Status": f"Success - The transcribe job: {job_name} has successfully started"}

            # Finally the response file will be written in the S3 bucket output folder.
            # Using S3 client to upload the response file
            s3.put_object(
                Bucket=bucket,
                Key=output_key,
                Body=json.dumps(response, default=string_converter)
            )

            return return_result
        except Exception as error:
            print(error)
            return {"Status": "Failed", "Reason": json.dumps(error, default=str)}

# Function to convert datetime to string.
def string_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
        
"""
You can use the code below to create a test event.
{
    "Records": [
                {
                "s3": {
                    "bucket": {
                    "name": "<Your_bucket_name>"
                    },
                    "object": {
                    "key": "input/sample_transcribe_1.mp3"
                    }
                }
                }
            ]
}
"""