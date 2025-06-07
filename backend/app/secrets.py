# backend/app/secrets.py

import boto3
import json

from botocore.exceptions import ClientError

def get_secrets():
    secret_name = "puybareau.wolfy"
    region_name = "eu-west-3"

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve secret: {e}")

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)