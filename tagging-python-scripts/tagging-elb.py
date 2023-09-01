import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "ELB"}
]

# AWS elbv2 client
elbv2_client = boto3.client('elbv2')


def tag_load_balancers():
    # Fetch load balancers
    load_balancers = elbv2_client.describe_load_balancers()['LoadBalancers']

    # Extract ARNs for tagging
    lb_arns = [lb['LoadBalancerArn'] for lb in load_balancers]
    success_count = 0

    for lb_arn in tqdm(lb_arns, desc="Load Balancers"):
        try:
            # Get existing tags for each load balancer
            existing_tags = elbv2_client.describe_tags(ResourceArns=[lb_arn])['TagDescriptions'][0]['Tags']
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the load balancer
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                elbv2_client.add_tags(ResourceArns=[lb_arn], Tags=tags)
                success_count += 1
        except Exception as e:
            print(f"Error tagging Load Balancer with ARN {lb_arn}: {e}")

    print(f"Load Balancers: Total={len(lb_arns)}, Successfully tagged={success_count}")


tag_load_balancers()
