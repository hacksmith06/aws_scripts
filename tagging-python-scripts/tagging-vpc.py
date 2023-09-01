import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "VPC"}
]

# AWS EC2 client (VPC is a part of the EC2 service in terms of AWS SDK)
ec2_client = boto3.client('ec2')


def tag_vpcs():
    # Fetch all VPCs
    vpcs = ec2_client.describe_vpcs()['Vpcs']

    # Extract VPC IDs for tagging
    vpc_ids = [vpc['VpcId'] for vpc in vpcs]
    success_count = 0

    for vpc_id in tqdm(vpc_ids, desc="VPCs"):
        try:
            # Get existing tags for each VPC
            existing_tags = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [vpc_id]}])['Tags']
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the VPC
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                ec2_client.create_tags(Resources=[vpc_id], Tags=tags)
                success_count += 1
        except Exception as e:
            print(f"Error tagging VPC with ID {vpc_id}: {e}")

    print(f"VPCs: Total={len(vpc_ids)}, Successfully tagged={success_count}")


tag_vpcs()
