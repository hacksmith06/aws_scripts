import boto3
import csv

# Create a session using your specific profile
session = boto3.Session(profile_name="qube")

# Now we use the session to create the client
s3 = session.client("s3")


def read_csv_file(filename):
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        data = list(reader)
    return data


def prepare_and_apply_tags(data):
    bucket_tags = {}

    for row in data:
        bucket_name = row["BucketName"]
        key = row["TagKey"]
        value = row["TagValue"]

        if bucket_name not in bucket_tags:
            bucket_tags[bucket_name] = []
        bucket_tags[bucket_name].append({"Key": key, "Value": value})

    for bucket_name, tags in bucket_tags.items():
        try:
            s3.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={"TagSet": tags},
            )
            print(f"Tags applied to bucket {bucket_name}")
        except Exception as e:
            print(f"Failed to apply tags to bucket {bucket_name}: {str(e)}")


data = read_csv_file("tags.csv")
prepare_and_apply_tags(data)
