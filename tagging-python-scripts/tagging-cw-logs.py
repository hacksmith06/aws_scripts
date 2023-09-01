import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "CloudWatchLog"}
]

# AWS CloudWatch Logs client
logs_client = boto3.client('logs')


def tag_cloudwatch_logs():
    # Fetch all CloudWatch Logs log groups
    log_groups = logs_client.describe_log_groups()['logGroups']

    success_count = 0

    for log_group in tqdm(log_groups, desc="CloudWatch Log Groups"):
        try:
            log_group_name = log_group['logGroupName']

            # Get existing tags for each log group
            existing_tags = logs_client.list_tags_log_group(logGroupName=log_group_name)['tags']
            existing_tag_keys = [key for key in existing_tags.keys()]

            # Check if tags already exist on the log group
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                logs_client.tag_log_group(logGroupName=log_group_name, tags={tag['Key']: tag['Value'] for tag in tags})
                success_count += 1
        except logs_client.exceptions.ResourceNotFoundException:
            # If the log group is not found, skip and continue
            print(f"CloudWatch Log Group {log_group_name} not found.")
        except Exception as e:
            print(f"Error tagging CloudWatch Log Group {log_group_name}: {e}")

    print(f"CloudWatch Log Groups: Total={len(log_groups)}, Successfully tagged={success_count}")


tag_cloudwatch_logs()
