# Make sure you have the `jq` tool installed, as this script uses it for JSON manipulation. 
# If it's not installed, you can get it using a package manager like apt, yum, or brew, or from the official website.

# List all S3 buckets and save the names to a file
aws s3api list-buckets --query "Buckets[*].[Name]" --output text > bucket-names.txt

# Loop through the names, get current tags, merge with new tags, and apply
while read -r bucket_name; do
    # Get existing tags
    current_tags=$(aws s3api get-bucket-tagging --bucket "$bucket_name" | jq -c '.TagSet')

    # If there are no existing tags, set current_tags to an empty list
    if [[ $? -ne 0 ]]; then
        current_tags="[]"
    fi

    # Merge new tags with existing tags, using `jq`
    merged_tags=$(echo $current_tags | jq -c 'map(select(.Key != "project" and .Key != "environment")) + [{"Key": "project", "Value": "Midmarket"}, {"Key": "environment", "Value": "production"}]')

    # Apply merged tags
    aws s3api put-bucket-tagging --bucket "$bucket_name" --tagging "TagSet=$merged_tags"
done < bucket-names.txt
