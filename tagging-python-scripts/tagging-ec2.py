import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "UAT"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "EC2"}
]

# AWS client
ec2_client = boto3.client('ec2')


def tag_resources(resource_type, resource_tag_value, describe_func, id_key_name):
    # Fetch resources
    resources = describe_func()

    if resource_type == "EC2 Instance":
        resources = [instance for reservation in resources for instance in reservation['Instances']]
    else:
        resources = resources

    # Extract IDs and tag
    resource_ids = [resource[id_key_name] for resource in resources]
    success_count = 0

    for resource_id in tqdm(resource_ids, desc=resource_type):
        try:
            existing_tags = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [resource_id]}])['Tags']
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the resource
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                ec2_client.create_tags(Resources=[resource_id], Tags=tags + [{"Key": "ResourceName", "Value": resource_tag_value}])
                success_count += 1
        except Exception as e:
            print(f"Error tagging {resource_type} {resource_id}: {e}")

    print(f"{resource_type}: Total={len(resource_ids)}, Successfully tagged={success_count}")


# Instances
tag_resources("EC2 Instance", "EC2Instance", lambda: ec2_client.describe_instances()['Reservations'], 'InstanceId')

# Volumes
tag_resources("EBS Volume", "EC2Volume", lambda: ec2_client.describe_volumes()['Volumes'], 'VolumeId')

# Elastic IPs
tag_resources("EIP", "EIP", lambda: ec2_client.describe_addresses()['Addresses'], 'AllocationId')

# Snapshots
tag_resources("Snapshot", "Snapshot", lambda: ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots'], 'SnapshotId')
