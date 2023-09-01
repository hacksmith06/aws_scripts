import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "Secret"}
]

# AWS Secrets Manager client
secrets_client = boto3.client('secretsmanager')


def tag_secrets_manager_secrets():
    # Fetch all secrets
    paginator = secrets_client.get_paginator('list_secrets')
    secrets = []
    for page in paginator.paginate():
        secrets.extend(page['SecretList'])

    success_count = 0

    for secret in tqdm(secrets, desc="Secrets"):
        try:
            secret_arn = secret['ARN']

            # Get existing tags for each secret
            existing_tags = secrets_client.describe_secret(SecretId=secret_arn).get('Tags', [])
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the secret
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                secrets_client.tag_resource(SecretId=secret_arn, Tags=tags)
                success_count += 1
        except secrets_client.exceptions.ResourceNotFoundException:
            # If the secret is not found, skip and continue
            print(f"Secret {secret_arn} not found.")
        except Exception as e:
            print(f"Error tagging Secret {secret_arn}: {e}")

    print(f"Secrets: Total={len(secrets)}, Successfully tagged={success_count}")


tag_secrets_manager_secrets()
