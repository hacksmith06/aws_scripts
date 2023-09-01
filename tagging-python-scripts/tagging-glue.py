import boto3
from tqdm import tqdm

# Define your tags
tags = {
    "HostLocation": "Mumbai",
    "Environment": "DEV",
    "ApplicationName": "MidMarket",
    "ResourceName": "Glue"
}

# AWS Glue client
glue_client = boto3.client('glue')


def tag_glue_databases():
    # Fetch all Glue databases
    paginator = glue_client.get_paginator('get_databases')
    databases = []
    for page in paginator.paginate():
        databases.extend(page['DatabaseList'])

    success_count = 0

    for database in tqdm(databases, desc="Glue Databases"):
        try:
            database_name = database['Name']

            # Get the ARN of the Glue database
            database_arn = database['CatalogArn']

            # Get existing tags for each database
            existing_tags = glue_client.get_tags(ResourceArn=database_arn)['Tags']

            # Check if tags already exist on the database
            tags_to_add = {k: v for k, v in tags.items() if k not in existing_tags}

            if tags_to_add:
                glue_client.tag_resource(ResourceArn=database_arn, TagsToAdd=tags_to_add)
                success_count += 1

        except glue_client.exceptions.EntityNotFoundException:
            # If the database is not found, skip and continue
            print(f"Glue Database {database_name} not found.")
        except Exception as e:
            print(f"Error tagging Glue Database {database_name}: {e}")

    print(f"Glue Databases: Total={len(databases)}, Successfully tagged={success_count}")


tag_glue_databases()
