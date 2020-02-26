
import schedule

from s3 import S3Handler
import paho.mqtt.client as mqtt
from config import Config

from datetime import datetime
from utils import *
import os 
import json
import time 

import shutil

ROOT_DIR = os.path.abspath('./')

class CronUploader():

    def __init__(self, rpi_config):
        self.s3 = S3Handler()
        self.mqttc = mqtt.Client()
        self.local_config = rpi_config._configuration_data 
        self.mqttc.username_pw_set(rpi_config.MQTT_USER, rpi_config.MQTT_PASS)
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.connect(rpi_config.MQTT_HOST, rpi_config.MQTT_PORT, rpi_config.MQTT_KEEP_ALIVE)
        self.rpi_id = os.environ['RPI_ID']

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))


    def on_message(self, mqttc, obj, msg):
        # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        pass

    def on_command(self, mqttc, obj, msg):
        print('Command topics')
        # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


    def on_publish(self, mqttc, obj, mid):
        # print("mid: " + str(mid))
        pass     

    def publish_message(self, topic, blob):
        result, mid = self.mqttc.publish(topic, blob, qos=0, retain=True)
        return result, mid

    def erase_files(self):
        print('Clear videos')
        
        local_path = self.local_config['location'] + '/' + os.environ['RPI_ID']
        if os.path.exists(local_path) and os.path.isdir(local_path):
            shutil.rmtree(local_path + '/')
        

    def upload(self):
        self.s3.upload_file_cron()
        



if __name__ == "__main__":

    
    while not internet():
        print('Waiting for internet connection')
        time.sleep(10)

    print('Connected to internet!')
    
    rpi_config = Config()

    c = CronUploader(rpi_config)

    erase_time = c.local_config['data']['erase_time']
    time_upload = c.local_config['data']['daily_upload_time']

    schedule.every().day.at(time_upload).do(c.upload)
    schedule.every().day.at(erase_time).do(c.erase_files)

    while 1:
        schedule.run_pending()
        time.sleep(1)