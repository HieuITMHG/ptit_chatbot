import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin_s3',         
    aws_secret_access_key='password_s3',  
    config=Config(s3={'addressing_style': 'path'})
)
