import boto3
from botocore.config import Config
from core.config import settings
from botocore.exceptions import ClientError

s3 = boto3.client(
    's3',
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.aws_access_key_id,         
    aws_secret_access_key=settings.aws_secret_access_key,  
    config=Config(s3={'addressing_style': 'path'}),
    region_name="us-east-1",
)

def ensure_bucket(s3, bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)

ensure_bucket(s3, settings.bucket_name)