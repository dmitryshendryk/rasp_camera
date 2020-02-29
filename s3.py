import logging
import boto3
from botocore.exceptions import ClientError
import os
from config import Config
import json

from datetime import datetime
import subprocess


ROOT_PATH = os.path.abspath('./')

class S3Handler():

    def __init__(self):
        self.configuration = Config()
        self.rpi_id = os.environ['RPI_ID']
        self.s3_client = boto3.client('s3', aws_access_key_id=self.configuration.aws_access_key_id,
                       aws_secret_access_key=self.configuration.aws_secret_access_key)
        
    def get_length(self, video_filename):
        videos_path = ROOT_PATH + '/' 
        video_filename = os.path.join(videos_path, video_filename)
        print("Get length {}".format(video_filename))
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of",
                                "default=noprint_wrappers=1:nokey=1", video_filename],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        try:
            return float(result.stdout)
        except ValueError:
            print(f'cannot extract length from {video_filename} - probably video is dark')
            return None

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

        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        blob = json.dumps({'time': str(now), 'region':mqtt.local_config['location'], 'node': mqtt.rpi_id, 'node_type': mqtt.local_config['type'], 'log': 'Manual Upload Started'})
        mqtt.publish_message('/logs/rpi/' + mqtt.local_config['type'] + '/', blob)
        
        for file_name in files:
            duration = self.get_length(file_name)
            path = file_name.split('/')
            file_name = path[-1].split('_')
            path.pop()
            duration = str(int(duration)) if duration else 'None'
            file_name = file_name[:7] + [duration] + file_name[7:]
            file_name = "_".join(file_name) 
            path += [file_name]
            path = "/".join(path)
            print("File {} duration is {}".format(path, duration))
            with open(path, "rb") as f:
                print('Uploading file {}'.format(path))
                blob = {}
                blob['connectionStatus'] = True
                mqtt.publish_message("/camera/uploading/" + mqtt.local_config['type'] +  '/' + mqtt.local_config['location'] + '/' + mqtt.rpi_id, json.dumps(blob))

                self.s3_client.upload_fileobj(f, "openlens-production", path)
                
                blob = {}
                blob['connectionStatus'] = False
                mqtt.publish_message("/camera/uploading/" + mqtt.local_config['type'] +  '/' + mqtt.local_config['location'] + '/' + mqtt.rpi_id, json.dumps(blob))

        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        blob = json.dumps({'time': str(now), 'region':mqtt.local_config['location'], 'node': mqtt.rpi_id, 'node_type': mqtt.local_config['type'], 'log': 'Manual Upload Finished'})
        mqtt.publish_message('/logs/rpi/' + mqtt.local_config['type'] + '/', blob)

        print("Finished uploading to S3")

# s3 = S3Handler()
# s3.upload_file()

