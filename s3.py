import logging
import boto3
from botocore.exceptions import ClientError
import os
from config import Config
import json

from datetime import datetime

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

    def upload_file_cron(self):
    
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
                self.s3_client.upload_fileobj(f, "openlens-production", file_name)
                
        print("Finished uploading to S3")

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


                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                blob = json.dumps({'time': str(now), 'region':mqtt.local_config['location'], 'node': mqtt.rpi_id, 'node_type': mqtt.local_config['type'], 'log': 'Cron Upload Started'})
                mqtt.publish_message('/logs/rpi/' + mqtt.local_config['type'] + '/', blob)


                self.s3_client.upload_fileobj(f, "openlens-production", file_name)
                
                blob['connectionStatus'] = False
                mqtt.publish_message("/camera/uploading/" + mqtt.local_config['type'] +  '/' + mqtt.local_config['location'] + '/' + mqtt.rpi_id, json.dumps(blob))

                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                blob = json.dumps({'time': str(now), 'region':mqtt.local_config['location'], 'node': mqtt.rpi_id, 'node_type': mqtt.local_config['type'], 'log': 'Cron Upload Finished'})
                mqtt.publish_message('/logs/rpi/' + mqtt.local_config['type'] + '/', blob)

        print("Finished uploading to S3")

# s3 = S3Handler()
# s3.upload_file()

