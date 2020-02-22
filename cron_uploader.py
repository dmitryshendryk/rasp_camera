
import schedule

from rpi_paramiko import SftpClient
import paho.mqtt.client as mqtt
from config import Config

from datetime import datetime
import os 
import json
import time 

ROOT_DIR = os.path.abspath('./')

class CronUploader():

    def __init__(self, rpi_config):
        self.ssh_paramiko = SftpClient()
        self.mqttc = mqtt.Client()
        self.local_config = rpi_config._configuration_data 
        self.mqttc.username_pw_set(rpi_config.MQTT_USER, rpi_config.MQTT_PASS)
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.connect(rpi_config.MQTT_HOST, rpi_config.MQTT_PORT, rpi_config.MQTT_KEEP_ALIVE)

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

    def upload(self):
        local_path = self.local_config['location'] + '/' + os.environ['RPI_ID']
        remote_path = '/home/ubuntu/videos/' 
        
        first_remote_level = remote_path + self.local_config['location']
        
        try:
            self.ssh_paramiko.chdir(first_remote_level)
        except IOError as e:
            print('Directory {0} doesnt exist'.format(first_remote_level))
            print('Create directory')
            self.ssh_paramiko.mkdir(first_remote_level)

        second_remote_level = remote_path + '/' +  self.local_config['location'] + '/' + os.environ['RPI_ID']
        
        try:
            self.ssh_paramiko.chdir(second_remote_level)
        except IOError as e:
            print('Directory {0} doesnt exist'.format(second_remote_level))
            print('Create directory')
            self.ssh_paramiko.mkdir(second_remote_level)

        print("Cron Upload videos to server")
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Cron starts upload files'})
        self.publish_message('/logs/rpi/' + self.local_config['type'] + '/', blob)

        no_file = False
        try:
            self.ssh_paramiko.put_dir(ROOT_DIR + '/' + local_path, second_remote_level)
        except Exception as e:
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'No files to upload'})
            self.publish_message('/logs/rpi/' + self.local_config['type'] + '/', blob)
            no_file = True 
            print(e)
        if not no_file:
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Cron Upload Finished'})
            self.publish_message('/logs/rpi/' + self.local_config['type'] + '/', blob)



if __name__ == "__main__":

    rpi_config = Config()

    c = CronUploader(rpi_config)

    schedule.every(1).minutes.do(c.upload)


    while 1:
        schedule.run_pending()
        time.sleep(1)