import boto3
from tqdm import tqdm

# Initialize a session/client for the ResourceGroupsTaggingAPI
client = boto3.client('resourcegroupstaggingapi')

# Define filters to narrow down the resources you want to tag (if needed)
# For tagging all resources, you can leave this empty or specify other filters
tag_filters = []

# Use get_resources to retrieve the resources based on filters
resources = client.get_resources(TagFilters=tag_filters)

# Define the three tags you want to apply to all resources
tags = [
    {
        'Key': 'Host Location',
        'Value': 'Mumbai'
    },
    {
        'Key': 'Environment',
        'Value': 'UAT'
    },
    {
        'Key': 'ApplicationName',
        'Value': 'EstatePlanning'
    }
]

# Initialize a tqdm progress bar with the total number of resources
progress_bar = tqdm(total=len(resources['ResourceTagMappingList']), desc='Tagging Resources')


# Helper function to check if a resource already has the specified tags
def has_tags(resource_tags, tags_to_check):
    return all(tag in resource_tags for tag in tags_to_check)


# Iterate through the resources and tag them
for resource in resources['ResourceTagMappingList']:
    resource_arn = resource['ResourceARN']

    try:
        # Check if the resource already has the specified tags
        existing_tags = client.get_resource_tags(ResourceARN=resource_arn)
        if not has_tags(existing_tags['Tags'], tags):
            # Tags are not present, so apply them
            client.tag_resources(ResourceARNList=[resource_arn], Tags=tags)
    except Exception as e:
        # Handle the exception (e.g., permission issue)
        print(f"Error tagging resource {resource_arn}: {str(e)}")

    # Update the progress bar
    progress_bar.update(1)

# Close the progress bar
progress_bar.close()
