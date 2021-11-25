import logging
import boto3
from botocore.exceptions import ClientError
import os

region_account = os.getenv('APP_SETTINGS_MODULE')
sso_region = os.getenv('SSO_REGION')
bucket_name_s3 = os.getenv('SSO_BUCKET_S3')
queue_name = os.getenv('QUEUE_NAME')
queue_url = os.getenv('SQS_QUEUE_URL')


def create_bucket():
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if sso_region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name_s3)
        else:
            s3_client = boto3.client('s3',
                                     region_name=sso_region)
            location = {'LocationConstraint': sso_region}
            s3_client.create_bucket(Bucket=bucket_name_s3,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def list_buckets():
    # Retrieve the list of existing buckets
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')


def upload_file(file_name, object_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client('s3',
                             region_name=sso_region)
    try:
        response = s3_client.upload_file(file_name, bucket_name_s3, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def downloading_files(file_name, object_name):
    s3 = boto3.client('s3',
                      region_name=sso_region)
    try:
        f = s3.download_file(bucket_name_s3, object_name, file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def get_object_name(file_name):
    return os.path.basename(file_name)


def remove_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    else:
        print('No se pudo remover el archivo')
        return 'No se pudo remover el archivo', 500


def find_object(object_name):
    s3 = boto3.resource('s3',
                        region_name=sso_region)
    bucket = s3.Bucket(bucket_name_s3)
    a = [x for x in bucket.objects.all() if x.key == object_name]
    if len(a) > 0:
        return True
    else:
        return False


def delete_object(object_name):
    s3 = boto3.resource('s3',
                        region_name=sso_region)
    try:
        s3.Object(bucket_name_s3, object_name).delete()
    except Exception as e:
        logging.error(e)
        return False
    return True

def existing_queue():
    # Get the service resource
    sqs = boto3.resource('sqs')

    # Get the queue. This returns an SQS.Queue instance
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    # You can now access identifiers and attributes
    print(queue.url)
    print(queue.attributes.get('DelaySeconds'))

    # Print out each queue name, which is part of its ARN
    for queue in sqs.queues.all():
        print(queue.url)

def send_message_queue(title,author,weeks,message):

    # Get the service resource
    sqs = boto3.resource('sqs')

    # Get the queue. This returns an SQS.Queue instance
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    # Send message to SQS queue
    response = queue.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            'Title': {
                'DataType': 'String',
                'StringValue': title
            },
            'Author': {
                'DataType': 'String',
                'StringValue': author
            },
            'WeeksOn': {
                'DataType': 'Number',
                'StringValue': weeks
            }
        },
        MessageBody=(message)
    )

    print('MessageId____________',response['MessageId'])

def receive_and_delete_messages_queue():

    # Create SQS client
    sqs = boto3.client('sqs')

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % message)