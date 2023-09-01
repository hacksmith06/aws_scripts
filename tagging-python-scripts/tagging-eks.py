import boto3
from tqdm import tqdm

# Define your tags
tags = {
    "HostLocation": "Mumbai",
    "Environment": "DEV",
    "ApplicationName": "MidMarket",
    "ResourceName": "EKS"
}

# AWS EKS client
eks_client = boto3.client('eks')


def tag_eks_clusters():
    # Fetch all EKS clusters
    clusters = eks_client.list_clusters()['clusters']

    success_count = 0

    for cluster_name in tqdm(clusters, desc="EKS Clusters"):
        try:
            # Get the ARN of the EKS cluster
            cluster = eks_client.describe_cluster(name=cluster_name)
            cluster_arn = cluster['cluster']['arn']

            # Get existing tags for each cluster
            existing_tags = eks_client.list_tags_for_resource(resourceArn=cluster_arn)['tags']

            # Check if tags already exist on the cluster
            tags_to_add = {k: v for k, v in tags.items() if k not in existing_tags}

            if tags_to_add:
                eks_client.tag_resource(resourceArn=cluster_arn, tags=tags_to_add)
                success_count += 1

        except eks_client.exceptions.ResourceNotFoundException:
            # If the cluster is not found, skip and continue
            print(f"EKS Cluster {cluster_name} not found.")
        except Exception as e:
            print(f"Error tagging EKS Cluster {cluster_name}: {e}")

    print(f"EKS Clusters: Total={len(clusters)}, Successfully tagged={success_count}")


tag_eks_clusters()
