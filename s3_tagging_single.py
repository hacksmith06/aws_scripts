import boto3


def apply_tags_to_buckets(bucket_names, tags):
    """
    Apply specified tags to the provided list of buckets.

    Parameters:
    - bucket_names (list): List of bucket names to which the tags should be applied.
    - tags (dict): Tags to be applied in the format {'Key': 'Value'}.
    """

    # Create a session using your specific profile
    session = boto3.Session(profile_name="qube")

    # Now we use the session to create the client
    s3 = session.client("s3")

    # Convert the tags dictionary to the format expected by Boto3
    tag_set = [{"Key": key, "Value": value} for key, value in tags.items()]

    for bucket_name in bucket_names:
        try:
            s3.put_bucket_tagging(Bucket=bucket_name, Tagging={"TagSet": tag_set})
            print(f"Tags applied to bucket: {bucket_name}")

        except Exception as e:
            print(f"Error applying tags to bucket {bucket_name}. Error: {e}")


bucket_names = ["sagemakerarpit"]
tags = {"createdby": "arpit"}
apply_tags_to_buckets(bucket_names, tags)
