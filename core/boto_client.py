import boto3
from botocore.config import Config
from core.config import settings

s3 = boto3.client(
    's3',
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.aws_access_key_id,         
    aws_secret_access_key=settings.aws_secret_access_key,  
    config=Config(s3={'addressing_style': 'path'})
)
