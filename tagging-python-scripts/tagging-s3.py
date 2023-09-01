import boto3
from tqdm import tqdm

# Define your tags
tags = {
    'TagSet': [
        {"Key": "HostLocation", "Value": "Mumbai"},
        {"Key": "Environment", "Value": "DEV"},
        {"Key": "ApplicationName", "Value": "MidMarket"},
        {"Key": "ResourceName", "Value": "S3"}
    ]
}

# AWS S3 client
s3_client = boto3.client('s3')


def tag_s3_buckets():
    # Fetch all S3 buckets
    buckets = s3_client.list_buckets()['Buckets']

    # Extract bucket names for tagging
    bucket_names = [bucket['Name'] for bucket in buckets]
    success_count = 0

    for bucket_name in tqdm(bucket_names, desc="S3 Buckets"):
        try:
            # Get existing tags for each bucket
            existing_tags = s3_client.get_bucket_tagging(Bucket=bucket_name).get('TagSet', [])
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the bucket
            if not all(tag['Key'] in existing_tag_keys for tag in tags['TagSet']):
                s3_client.put_bucket_tagging(Bucket=bucket_name, Tagging=tags)
                success_count += 1
        except s3_client.exceptions.NoSuchTagSet:
            # If no tags exist on the bucket, apply tags directly
            s3_client.put_bucket_tagging(Bucket=bucket_name, Tagging=tags)
            success_count += 1
        except Exception as e:
            print(f"Error tagging S3 bucket {bucket_name}: {e}")

    print(f"S3 Buckets: Total={len(bucket_names)}, Successfully tagged={success_count}")


tag_s3_buckets()
