##Ensure you have jq installed, as it's used for JSON processing.
# # Resources that will be tagged
# 1. EC2 
# 2. EBS Volumes
# 3. Load Balancers
# 4. Elastic IPs
# 5. Snapshots

# Initialize counters
declare -A count
declare -A successCount

# Define tags here
declare -A tags
tags[HostLocation]=""
tags[Environment]=""
tags[ApplicationName]=""
tags[ResourceName]=""


# Function to tag resources
tag_resources() {
    local resourceType="$1"
    local query="$2"
    local resourceTagValue="$3" # The value for the 'ResourceName' tag
    local outputFile="$resourceType-ids.txt"

    # Set the specific ResourceName tag for this resource type
    tags[ResourceName]=$resourceTagValue

    # Convert associative array of tags to AWS CLI tag format
    local tagArgs=""
    for key in "${!tags[@]}"; do
        tagArgs="$tagArgs Key=$key,Value=${tags[$key]}"
    done

    # List resources
    aws ec2 describe-$resourceType --query "$query" --output text > "$outputFile"
    count[$resourceType]=$(wc -l < "$outputFile")

    # Loop through the resources and apply tags
    local success=0
    while read -r resourceId; do
        aws ec2 create-tags --resources "$resourceId" --tags $tagArgs && success=$((success + 1))
    done < "$outputFile"
    successCount[$resourceType]=$success
}

# Call the function for each resource type
tag_resources "instances" "Reservations[*].Instances[*].[InstanceId]" "EC2Instance"
tag_resources "volumes" "Volumes[*].[VolumeId]" "EC2Volume"
tag_resources "addresses" "Addresses[*].[AllocationId]" "EIP"
tag_resources "snapshots" "Snapshots[*].[SnapshotId]" "Snapshot"

# For Load Balancers (a bit different due to needing merged tags)
lb_outputFile="loadbalancer-arns.txt"
aws elbv2 describe-load-balancers --query "LoadBalancers[*].[LoadBalancerArn]" --output text > "$lb_outputFile"
count["loadbalancers"]=$(wc -l < "$lb_outputFile")
success=0
while read -r lb_arn; do
    current_tags=$(aws elbv2 describe-tags --resource-arns "$lb_arn" | jq -c '.TagDescriptions[0].Tags')
    if [[ -z "$current_tags" || "$current_tags" == "null" ]]; then
        current_tags="[]"
    fi
    merged_tags=$(echo $current_tags | jq -c 'map(select(.Key != "project" and .Key != "environment")) + [{"Key": "project", "Value": "Midmarket"}, {"Key": "environment", "Value": "production"}]')
    aws elbv2 add-tags --resource-arns "$lb_arn" --tags "$merged_tags" && success=$((success + 1))
done < "$lb_outputFile"
successCount["loadbalancers"]=$success
echo "loadbalancers: Total=${count[loadbalancers]}, Successfully tagged=${successCount[loadbalancers]}"

# Print out the results
for resourceType in "${!count[@]}"; do
    echo "$resourceType: Total=${count[$resourceType]}, Successfully tagged=${successCount[$resourceType]}"
done
