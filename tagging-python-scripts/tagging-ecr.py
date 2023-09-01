import boto3
from tqdm import tqdm

# Define your tags
tags = [
    {"Key": "HostLocation", "Value": "Mumbai"},
    {"Key": "Environment", "Value": "DEV"},
    {"Key": "ApplicationName", "Value": "MidMarket"},
    {"Key": "ResourceName", "Value": "ECR"}
]

# AWS ECR client
ecr_client = boto3.client('ecr')


def tag_ecr_repositories():
    # Fetch all ECR repositories
    repositories = ecr_client.describe_repositories()['repositories']
    success_count = 0

    for repo in tqdm(repositories, desc="ECR Repositories"):
        try:
            repo_name = repo['repositoryName']
            repo_arn = repo['repositoryArn']  # Extract ARN directly from the repository data

            # Get existing tags for each repository
            existing_tags = ecr_client.list_tags_for_resource(resourceArn=repo_arn)['tags']
            existing_tag_keys = [tag['Key'] for tag in existing_tags]

            # Check if tags already exist on the repository
            if not all(tag['Key'] in existing_tag_keys for tag in tags):
                ecr_client.tag_resource(resourceArn=repo_arn, tags=tags)
                success_count += 1
        except ecr_client.exceptions.RepositoryNotFoundException:
            # If the repository is not found, skip and continue
            print(f"ECR Repository {repo_name} not found.")
        except Exception as e:
            print(f"Error tagging ECR repository {repo_name}: {e}")

    print(f"ECR Repositories: Total={len(repositories)}, Successfully tagged={success_count}")


tag_ecr_repositories()
