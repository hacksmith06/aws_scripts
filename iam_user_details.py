import boto3
import pytz
import csv
from tqdm import tqdm  # Import tqdm


# Convert UTC datetime to IST
def convert_to_ist(utc_dt):
    ist = pytz.timezone("Asia/Kolkata")
    return utc_dt.astimezone(ist)


# Create a session using your specific profile
session = boto3.Session(profile_name="qube")

# Now we use the session to create the clients
iam = session.client("iam")

# Create CSV file and writer
with open("IAM_users_info.csv", "w", newline="") as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(
        [
            "Username",
            "UserID",
            "User ARN",
            "User Creation Time",
            "Permissions Boundary",
            "Password Last Used",
            "Tags",
            "MFA Devices",
            "Login Profile Exists",
            "Groups",
            "Managed Policies",
            "Inline Policies",
            "Access Key ID",
            "Access Key Status",
            "Access Key Last Used Date",
        ]
    )

    # List users
    response = iam.list_users()
    users = response["Users"]

    for user in tqdm(users, desc="Processing Users", unit="user"):
        username = user["UserName"]
        user_id = user["UserId"]
        user_arn = user["Arn"]
        user_creation_time = convert_to_ist(user["CreateDate"])

        # Get user for more details
        user_details = iam.get_user(UserName=username)
        permissions_boundary = (
            user_details["User"]
            .get("PermissionsBoundary", {})
            .get("PermissionsBoundaryArn", "None")
        )
        password_last_used = user_details["User"].get(
            "PasswordLastUsed", "Password not used"
        )
        if password_last_used != "Password not used":
            password_last_used = convert_to_ist(password_last_used)

        # Get user tags
        tags_response = iam.list_user_tags(UserName=username)
        tags = {tag["Key"]: tag["Value"] for tag in tags_response["Tags"]}

        # List MFA devices
        mfa_devices_response = iam.list_mfa_devices(UserName=username)
        mfa_devices = [
            mfa_device["SerialNumber"]
            for mfa_device in mfa_devices_response["MFADevices"]
        ]

        # Get login profile
        try:
            login_profile_response = iam.get_login_profile(UserName=username)
            login_profile_exists = True
        except iam.exceptions.NoSuchEntityException:
            login_profile_exists = False

        # List groups for user
        groups_response = iam.list_groups_for_user(UserName=username)
        groups = [group["GroupName"] for group in groups_response["Groups"]]

        # List managed policies
        managed_policies_response = iam.list_attached_user_policies(UserName=username)
        managed_policies = [
            policy["PolicyName"]
            for policy in managed_policies_response["AttachedPolicies"]
        ]

        # List inline policies
        inline_policies_response = iam.list_user_policies(UserName=username)
        inline_policies = inline_policies_response["PolicyNames"]

        # List access keys
        access_keys_response = iam.list_access_keys(UserName=username)
        access_keys = access_keys_response["AccessKeyMetadata"]

        for key in access_keys:
            access_key_id = key["AccessKeyId"]
            access_key_status = key["Status"]

            # Get the last used date for the access key
            last_used_response = iam.get_access_key_last_used(AccessKeyId=access_key_id)
            last_used_info = last_used_response["AccessKeyLastUsed"]
            last_used_date = last_used_info.get("LastUsedDate", "Never Used")
            if last_used_date != "Never Used":
                last_used_date = convert_to_ist(last_used_date).isoformat()

            # Write user data to CSV
            writer.writerow(
                [
                    username,
                    user_id,
                    user_arn,
                    user_creation_time.isoformat(),
                    permissions_boundary,
                    password_last_used.isoformat()
                    if password_last_used != "Password not used"
                    else password_last_used,
                    tags,
                    mfa_devices,
                    login_profile_exists,
                    groups,
                    managed_policies,
                    inline_policies,
                    access_key_id,
                    access_key_status,
                    last_used_date,
                ]
            )
