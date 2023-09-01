# # Resources that will be tagged
# 1. EC2 
# 2. EBS Volumes
# 3. S3

# List all EC2 instances and save the IDs to a file
aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId]" --output text > instance-ids.txt

# Loop through the IDs and apply tags
while read -r instance_id; do
    aws ec2 create-tags --resources "$instance_id" \
        --tags Key=project,Value=Midmarket Key=environment,Value=production
done < instance-ids.txt




