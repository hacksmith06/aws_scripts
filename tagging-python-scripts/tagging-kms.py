import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"TagKey": "HostLocation", "TagValue": "Mumbai"},
    {"TagKey": "Environment", "TagValue": "DEV"},
    {"TagKey": "ApplicationName", "TagValue": "MidMarket"},
    {"TagKey": "ResourceName", "TagValue": "KMS"}
]

# AWS KMS client
kms_client = boto3.client('kms')


def tag_kms_keys():
    # Fetch all KMS keys
    keys = kms_client.list_keys()['Keys']

    # Extract key ids for tagging
    key_ids = [key['KeyId'] for key in keys]
    success_count = 0

    for key_id in tqdm(key_ids, desc="KMS Keys"):
        try:
            # Get existing tags for each key
            existing_tags = kms_client.list_resource_tags(KeyId=key_id)['Tags']
            existing_tag_keys = [tag['TagKey'] for tag in existing_tags]

            # Check if tags already exist on the key
            if not all(tag['TagKey'] in existing_tag_keys for tag in tags):
                kms_client.tag_resource(KeyId=key_id, Tags=tags)
                success_count += 1
        except kms_client.exceptions.NotFoundException:
            # If the key is not found, skip and continue
            print(f"KMS Key {key_id} not found.")
        except Exception as e:
            print(f"Error tagging KMS key {key_id}: {e}")

    print(f"KMS Keys: Total={len(key_ids)}, Successfully tagged={success_count}")


tag_kms_keys()
