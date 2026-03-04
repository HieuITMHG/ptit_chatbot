import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin',         
    aws_secret_access_key='admin123',  
    region_name='us-east-1',
    config=Config(s3={'addressing_style': 'path'})
)