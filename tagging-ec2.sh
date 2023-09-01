# # Resources that will be tagged
# 1. EC2 
# 2. EBS Volumes
# 3. Load Balancers

# List all EC2 instances and save the IDs to a file
aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId]" --output text > instance-ids.txt

# Loop through the IDs and apply tags
while read -r instance_id; do
    aws ec2 create-tags --resources "$instance_id" \
        --tags Key=project,Value=Midmarket Key=environment,Value=production
done < instance-ids.txt

# List all EBS volumes and save the IDs to a file
aws ec2 describe-volumes --query "Volumes[*].[VolumeId]" --output text > volume-ids.txt

# Loop through the IDs and apply tags
while read -r volume_id; do
    aws ec2 create-tags --resources "$volume_id" \
        --tags Key=project,Value=Midmarket Key=environment,Value=production
done < volume-ids.txt

# List all Load Balancers (Application and Network Load Balancers) and save the ARNs to a file
aws elbv2 describe-load-balancers --query "LoadBalancers[*].[LoadBalancerArn]" --output text > loadbalancer-arns.txt

# Loop through the ARNs, get current tags, merge with new tags, and apply
while read -r lb_arn; do
    # Get existing tags
    current_tags=$(aws elbv2 describe-tags --resource-arns "$lb_arn" | jq -c '.TagDescriptions[0].Tags')

    # If there are no existing tags, set current_tags to an empty list
    if [[ -z "$current_tags" || "$current_tags" == "null" ]]; then
        current_tags="[]"
    fi

    # Merge new tags with existing tags, using `jq`
    merged_tags=$(echo $current_tags | jq -c 'map(select(.Key != "project" and .Key != "environment")) + [{"Key": "project", "Value": "Midmarket"}, {"Key": "environment", "Value": "production"}]')

    # Apply merged tags
    aws elbv2 add-tags --resource-arns "$lb_arn" --tags "$merged_tags"
done < loadbalancer-arns.txt


