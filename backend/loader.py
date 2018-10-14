import boto3
import json
import os
import numpy as np
from botocore import UNSIGNED
from botocore.client import Config

s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
S3_BUCKET = 'insta-image-search'

def read_s3_file(key):
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        return response['Body'].read().decode()

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.\
        Make sure they exist and your bucket is in the same region as this function.'.format(key, S3_BUCKET))
        return None


def load_image_data_file(path):
    # first, look for the data in the local data directory
    data = None
    try:
        data = open('data/' + path, 'r+').read()
    except FileNotFoundError as e:
        data = None
    # cant find it, load it from s3
    if data == None:
        print('Downloading from S3...')
        data = read_s3_file(path)
        if not os.path.exists('data'):
            os.makedirs('data')
        open('data/%s' % path, 'w+').write(data)
    return json.loads(data)

def get_image_data_filenames():
    return [obj['Key'] for obj in s3_client.list_objects(Bucket=S3_BUCKET)['Contents']]

def load_image_data():
    data = []
    for path in get_image_data_filenames():
        print('loading %s...' % path)
        data += load_image_data_file(path)
        print('done')

    for i in range(len(data)):
        data[i]['image_vector'] = np.asfarray(data[i]['image_vector'])
    return data
