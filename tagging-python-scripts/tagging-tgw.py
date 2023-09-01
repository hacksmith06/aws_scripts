import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "TGW"}
]

# AWS EC2 client (Even though we're working with Transit Gateways, they're part of the EC2 service in terms of AWS SDK)
ec2_client = boto3.client('ec2')


def tag_transit_gateways():
    # Fetch all Transit Gateways
    transit_gateways = ec2_client.describe_transit_gateways()['TransitGateways']

    # Extract Transit Gateway IDs for tagging
    tgw_ids = [tgw['TransitGatewayId'] for tgw in transit_gateways]
    success_count = 0

    for tgw_id in tqdm(tgw_ids, desc="Transit Gateways"):
        try:
            # Get existing tags for each Transit Gateway
            existing_tags = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [tgw_id]}])['Tags']
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the Transit Gateway
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                ec2_client.create_tags(Resources=[tgw_id], Tags=tags)
                success_count += 1
        except Exception as e:
            print(f"Error tagging Transit Gateway with ID {tgw_id}: {e}")

    print(f"Transit Gateways: Total={len(tgw_ids)}, Successfully tagged={success_count}")


tag_transit_gateways()
