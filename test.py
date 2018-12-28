# test.py
# Created to test boto3 and uploading to AWS S3

import boto3
import uuid

def create_bucket_name(bucket_prefix):
    # The generated bucket name must be between 3 and 63 chars long
    return ''.join([bucket_prefix, str(uuid.uuid4())])

def create_bucket(bucket_prefix, s3_connection):
    session = boto3.session.Session()
    current_region = session.region_name
    bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': current_region}
            )
    print(bucket_name, current_region)
    return bucket_name, bucket_response

s3_client = boto3.client('s3')
s3_client.upload_file(
            Filename='./Hanako.png', Bucket='jackson56a4fac2-0705-4d37-88d6-8582757e9b8c',
            Key='Pictures/Hanako.png')
