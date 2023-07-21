import boto3
import pytz
import csv
from tqdm import tqdm  # Import tqdm

# Create a session using your specific profile
session = boto3.Session(profile_name="qube")

# Now we use the session to create the client
s3 = session.client("s3")

# Define the time zone
ist = pytz.timezone("Asia/Kolkata")


def get_bucket_size_and_object_count(bucket_name):
    paginator = s3.get_paginator("list_objects_v2")
    size = 0
    object_count = 0
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            size += obj["Size"]
            object_count += 1
    # Convert size from bytes to Megabytes
    size_in_mb = size / (1024 * 1024)
    return size_in_mb, object_count


# Function to get the last used date of the bucket
def get_last_used_date(bucket_name):
    response = s3.list_objects_v2(Bucket=bucket_name)
    if "Contents" not in response:
        return None
    last_modified_dates = [content["LastModified"] for content in response["Contents"]]
    return max(last_modified_dates) if last_modified_dates else None


# Function to get the tags of the bucket
def get_bucket_tags(bucket_name):
    try:
        response = s3.get_bucket_tagging(Bucket=bucket_name)
        tags = response["TagSet"]
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchTagSet":
            tags = None
        else:
            raise
    return tags


# Function to convert UTC to IST
def utc_to_ist(utc_dt):
    """Convert UTC datetime to IST and return as string."""
    if not utc_dt:
        return None
    ist_dt = utc_dt.astimezone(ist)
    return ist_dt.strftime("%Y-%m-%d %H:%M:%S")


def get_server_side_encryption(bucket_name):
    try:
        response = s3.get_bucket_encryption(Bucket=bucket_name)
        encryption = response.get("ServerSideEncryptionConfiguration")
        return encryption is not None
    except s3.exceptions.ClientError as e:
        if (
            e.response["Error"]["Code"]
            == "ServerSideEncryptionConfigurationNotFoundError"
        ):
            encryption = None
        else:
            raise


def get_object_lock(bucket_name):
    try:
        response = s3.get_object_lock_configuration(Bucket=bucket_name)
        return response.get("ObjectLockConfiguration")
    except s3.exceptions.ClientError:
        return None


def check_public_access(bucket_name):
    try:
        response = s3.get_bucket_policy_status(Bucket=bucket_name)
        is_public = response["PolicyStatus"]["IsPublic"]
        return is_public
    except s3.exceptions.ClientError:
        return False


buckets_info = []

for bucket in tqdm(
    s3.list_buckets()["Buckets"], desc="Processing Buckets", unit="bucket"
):
    bucket_name = bucket["Name"]
    creation_date = bucket["CreationDate"]

    # Get the last used date
    last_used_on = get_last_used_date(bucket_name)

    # Get versioning info
    versioning = s3.get_bucket_versioning(Bucket=bucket_name)
    version_status = versioning.get("Status", "Not Enabled")

    # Get logging info
    logging = s3.get_bucket_logging(Bucket=bucket_name)
    logging_status = logging.get("LoggingEnabled", None)

    # Get tags info
    tags = get_bucket_tags(bucket_name)

    # Convert times from UTC to IST
    creation_date = utc_to_ist(creation_date)
    last_used_on = utc_to_ist(last_used_on)

    encryption = get_server_side_encryption(bucket_name)
    object_lock = get_object_lock(bucket_name)
    public_access = check_public_access(bucket_name)

    # Get bucket size and object count
    size, object_count = get_bucket_size_and_object_count(bucket_name)

    bucket_data = {
        "Name": bucket_name,
        "Creation Date": creation_date,
        "Last Used On": last_used_on,
        "Versioning": version_status,
        "Logging": logging_status,
        "Tags": tags,
        "Server-Side Encryption": encryption,
        "Object Lock": object_lock,
        "Public Access": public_access,
        "Size": size,
        "Object Count": object_count,
    }

    buckets_info.append(bucket_data)


# Define CSV file columns
csv_columns = [
    "Name",
    "Creation Date",
    "Last Used On",
    "Versioning",
    "Logging",
    "Tags",
    "Server-Side Encryption",
    "Object Lock",
    "Public Access",
    "Size",
    "Object Count",
]

# Write data to CSV file
with open("buckets_info.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data in buckets_info:
        writer.writerow(data)

print("Data written to 'buckets_info.csv'")
