import boto3
import csv

# Set up AWS session and EC2 resources
session = boto3.Session(region_name='ap-south-1')
ec2 = session.resource('ec2')
ec2_client = session.client('ec2')


# Function to fetch status checks
def get_status_checks(instance_id):
    checks = ec2_client.describe_instance_status(InstanceIds=[instance_id])
    if checks['InstanceStatuses']:
        system_status = checks['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']
        instance_status = checks['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status']
    else:
        system_status, instance_status = 'N/A', 'N/A'
    return system_status, instance_status


# Write to CSV
with open('ec2_instances.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Instance ID", "State", "Instance Type",
                     "Launch Time", "System Status", "Instance Status"])
    for instance in ec2.instances.all():
        system_status, instance_status = get_status_checks(instance.id)
        writer.writerow([
            instance.id, instance.state['Name'], instance.instance_type,
            instance.launch_time, system_status, instance_status
        ])
