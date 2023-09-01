import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "RDS"}
]

# AWS RDS client
rds_client = boto3.client('rds')


def tag_rds_instances():
    # Fetch all RDS instances
    rds_instances = rds_client.describe_db_instances()['DBInstances']

    # Extract RDS instance IDs (ARNs) for tagging
    rds_instance_arns = [instance['DBInstanceArn'] for instance in rds_instances]
    success_count = 0

    for rds_instance_arn in tqdm(rds_instance_arns, desc="RDS Instances"):
        try:
            # Get existing tags for each RDS instance
            existing_tags = rds_client.list_tags_for_resource(ResourceName=rds_instance_arn)['TagList']
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the RDS instance
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                rds_client.add_tags_to_resource(ResourceName=rds_instance_arn, Tags=tags)
                success_count += 1
        except Exception as e:
            print(f"Error tagging RDS instance with ARN {rds_instance_arn}: {e}")

    print(f"RDS Instances: Total={len(rds_instance_arns)}, Successfully tagged={success_count}")


tag_rds_instances()
