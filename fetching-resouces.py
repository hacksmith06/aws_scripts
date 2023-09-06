import boto3
from tqdm import tqdm

# Initialize a session/client for the ResourceGroupsTaggingAPI
client = boto3.client('resourcegroupstaggingapi')

# Define filters to narrow down the resources you want to fetch
# In this example, we'll fetch resources with names containing 'ec2'
resource_filter = {
    'Key': 'Name',
    'Values': ['*ec2*']
}

# Use get_resources to retrieve the resources based on filters
resources = client.get_resources(Filters=[resource_filter])

# Initialize a tqdm progress bar with the total number of resources
progress_bar = tqdm(total=len(resources['ResourceTagMappingList']), desc='Fetching Resources')

# Iterate through the fetched resources and print their ARNs
for resource in resources['ResourceTagMappingList']:
    resource_arn = resource['ResourceARN']
    print(resource_arn)
    
    # Update the progress bar
    progress_bar.update(1)

# Close the progress bar
progress_bar.close()
