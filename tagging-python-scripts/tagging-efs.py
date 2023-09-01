import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "EFS"}
]

# AWS EFS client
efs_client = boto3.client('efs')


def tag_efs_filesystems():
    # Fetch all EFS file systems
    filesystems = efs_client.describe_file_systems()['FileSystems']

    success_count = 0

    for fs in tqdm(filesystems, desc="EFS File Systems"):
        try:
            fs_id = fs['FileSystemId']

            # Get existing tags for each file system
            existing_tags = efs_client.describe_tags(FileSystemId=fs_id)['Tags']
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the file system
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                efs_client.create_tags(FileSystemId=fs_id, Tags=tags)
                success_count += 1
        except efs_client.exceptions.FileSystemNotFound:
            # If the file system is not found, skip and continue
            print(f"EFS File System {fs_id} not found.")
        except Exception as e:
            print(f"Error tagging EFS File System {fs_id}: {e}")

    print(f"EFS File Systems: Total={len(filesystems)}, Successfully tagged={success_count}")


tag_efs_filesystems()
