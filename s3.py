import logging
import boto3
from botocore.exceptions import ClientError
import os
from config import Config
import json


class S3Handler():

    def __init__(self):
        self.configuration = Config()
        self.rpi_id = 'test'
        self.s3_client = boto3.client('s3', aws_access_key_id=self.configuration.aws_access_key_id,
                       aws_secret_access_key=self.configuration.aws_secret_access_key)
        


    def get_files_path(self, path):

        paths = []
        dirs = set()
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                paths.append(os.path.join(dirname, filename))
                dirs.add(dirname)
        
        return paths,  sorted(list(dirs), key=lambda x: len(x))


    def is_folder_exist(self, path):

        result = self.s3_client.list_objects(Bucket=self.configuration.s3_bucket_name, Prefix=path)
        return 'Contents' in result


    def create_folder(self, path):
        self.s3_client.put_object(Bucket=self.configuration.s3_bucket_name, Key=(path +'/'))

    def upload_file(self, mqtt):
    
        print("Start uploading to S3")
        location = self.configuration._configuration_data['location']
        
        files, dirs = self.get_files_path(location)
        
        for d in dirs:
            if not self.is_folder_exist(d):
                
                print('Create folder {}'.format(d))
                self.create_folder(d)
            else:
                print("{} is exists".format(d))


        for file_name in files:
            with open(file_name, "rb") as f:
                print('Uploading file {}'.format(file_name))
                blob = {}
                blob['connectionStatus'] = True
                mqtt.publish_message("/camera/uploading/" + mqtt.local_config['type'] +  '/' + mqtt.local_config['location'] + '/' + mqtt.rpi_id, json.dumps(blob))
                self.s3_client.upload_fileobj(f, "openlens-production", file_name)
                
                blob['connectionStatus'] = False
                mqtt.publish_message("/camera/uploading/" + mqtt.local_config['type'] +  '/' + mqtt.local_config['location'] + '/' + mqtt.rpi_id, json.dumps(blob))
        print("Finished uploading to S3")

# s3 = S3Handler()
# s3.upload_file()

