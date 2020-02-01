import paho.mqtt.client as mqtt
from config import Config
import subprocess
import os 
from rpi_paramiko import SftpClient
import shutil
import json


from error import CameraNotConnected
from datetime import datetime

ROOT_DIR = os.path.abspath('./')

class MQTTClient():

    def __init__(self, camera_obj):
        self.ssh_paramiko = SftpClient()
        self.config = Config()
        self.local_config = None 
        self.mqttc = mqtt.Client()
        self.mqttc.username_pw_set(Config.MQTT_USER, Config.MQTT_PASS)
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.connect(Config.MQTT_HOST, Config.MQTT_PORT, Config.MQTT_KEEP_ALIVE)
        self.camera = None
        self.rpi_id = os.environ['RPI_ID']
        try:
            self.camera = camera_obj
        except CameraNotConnected as e:
            print('Camera not connected __init__')
        
        try:
            with open('./cfg/configuration.json', 'r') as f:
                self.local_config = json.load(f)
        except ValueError:
            print('JSON read error')

        self.mqttc.subscribe("store/prishna/rpi/actions/reboot", qos=1)
        self.mqttc.subscribe("store/prishna/rpi/actions/shutdown", qos=1)
        self.mqttc.subscribe("store/prishna/rpi/actions/start_video", qos=1)
        self.mqttc.subscribe("store/prishna/rpi/actions/stop_video", qos=1)
        self.mqttc.subscribe("store/prishna/rpi/actions/clear_videos", qos=1)
        self.mqttc.subscribe("store/prishna/rpi/actions/upload_videos", qos=1)
        self.mqttc.subscribe("store/prishna/rpi/actions/auto", qos=1)

        self.mqttc.message_callback_add("store/prishna/rpi/actions/reboot", self.reboot_rpi)
        self.mqttc.message_callback_add("store/prishna/rpi/actions/shutdown", self.shutdown_rpi)
        self.mqttc.message_callback_add("store/prishna/rpi/actions/start_video", self.start_video_recording)
        self.mqttc.message_callback_add("store/prishna/rpi/actions/stop_video", self.stop_video_recording)
        self.mqttc.message_callback_add("store/prishna/rpi/actions/clear_videos", self.clear_videos)
        self.mqttc.message_callback_add("store/prishna/rpi/actions/upload_videos", self.upload_video_to_server)
        self.mqttc.message_callback_add("store/prishna/rpi/actions/auto", self.automode)


    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))


    def on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_command(self, mqttc, obj, msg):
        print('Command topics')
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))


    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))


    def on_log(self, mqttc, obj, level, string):
        print(string)

    def publish_message(self, topic, blob):
        result, mid = self.mqttc.publish(topic, blob, qos=0, retain=True)
        return result, mid


    def reboot_rpi(self, mqttc, obj, msg):
        msg = json.loads(msg.payload)
        print(msg)
        if self.rpi_id == msg['rpi_id'] and self.local_config['type'] == msg['type']:
            bashCommand = 'echo ' + os.environ['RPI_PASS'] + ' | sudo -S reboot'
            subprocess.call(bashCommand, shell=True)
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'reboot RPI'})
            self.publish_message('/logs/rpi/' + self.local_config['type'] +  '/' + str(self.rpi_id) , blob)
    
    def shutdown_rpi(self, mqttc, obj, msg):
        msg = json.loads(msg.payload)
        print(msg)
        if self.rpi_id == msg['rpi_id'] and self.local_config['type'] == msg['type']:
            bashCommand = 'echo ' + os.environ['RPI_PASS'] + ' | sudo -S shutdown -h now'
            subprocess.call(bashCommand, shell=True)
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'shutdown RPI'})
            self.publish_message('/logs/rpi/' + self.local_config['type'] +  '/' + str(self.rpi_id), blob)

    def start_video_recording(self, mqttc, obj, msg):
        if self.camera:
            msg = json.loads(msg.payload)
            print(msg)
            if self.rpi_id == msg['rpi_id'] and self.local_config['type'] == msg['type']:
                print('Start video recording')
                self.camera.start(self)
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Start Recording Video'})
                self.publish_message('/logs/rpi/' + self.local_config['type'] +  '/' + str(self.rpi_id), blob)
        else:
            print('Camera not connected start_video_recording')

    def automode(self, mqttc, obj, mwg):
        if self.camera:
            msg = json.loads(msg.payload)
            print(msg)
            if self.rpi_id == msg['rpi_id'] and self.local_config['type'] == msg['type']:
                print('Start automode')
                

    def stop_video_recording(self, mqttc, obj, msg):
        if self.camera:
            msg = json.loads(msg.payload)
            print(msg)
            if self.rpi_id == msg['rpi_id'] and self.local_config['type'] == msg['type']:
                print('Stop video recording')
                self.camera.stop(self)
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Stop Recording Video'})
                self.publish_message('/logs/rpi/' + self.local_config['type'] +  '/' + str(self.rpi_id), blob)
        else:
            print('Camera not connected stop_video_recording')
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Camera Not Connected'})
            self.publish_message('/logs/rpi/' + + self.local_config['type'] +  '/' + str(self.rpi_id), {'time': now, 'log': 'Camera Not Connected'})

    def upload_video_to_server(self,mqttc, obj, msg):
        msg = json.loads(msg.payload)
        print(msg)
        if self.rpi_id == msg['rpi_id'] and self.local_config['type'] == msg['type']:
            local_path = self.config._configuration_data['location'] + '/' + os.environ['RPI_ID']
            remote_path = '/home/ubuntu/videos/' 
            
            first_remote_level = remote_path + self.config._configuration_data['location']
            
            try:
                self.ssh_paramiko.chdir(first_remote_level)
            except IOError as e:
                print('Directory {0} doesnt exist'.format(first_remote_level))
                print('Create directory')
                self.ssh_paramiko.mkdir(first_remote_level)

            second_remote_level = remote_path + '/' +  self.config._configuration_data['location'] + '/' + os.environ['RPI_ID']
            
            try:
                self.ssh_paramiko.chdir(second_remote_level)
            except IOError as e:
                print('Directory {0} doesnt exist'.format(second_remote_level))
                print('Create directory')
                self.ssh_paramiko.mkdir(second_remote_level)

            print("Upload videos to server")
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Upload Video to Server'})
            self.publish_message('/logs/rpi/' +  self.local_config['type'] +  '/' + str(self.rpi_id), blob)
            self.ssh_paramiko.put_dir(ROOT_DIR + '/' + local_path, second_remote_level)
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Upload Finished'})
            self.publish_message('/logs/rpi/' + self.local_config['type'] +  '/' + str(self.rpi_id), blob)
    
    def clear_videos(self,mqttc, obj, msg):
        msg = json.loads(msg.payload)
        print(msg)
        if self.rpi_id == msg['rpi_id'] and self.local_config['type'] == msg['type']:
            print('CLear videos')
            
            local_path = self.config._configuration_data['location'] + '/' + os.environ['RPI_ID']
            if os.path.exists(local_path) and os.path.isdir(local_path):
                shutil.rmtree(local_path + '/')
            
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            blob = json.dumps({'time': str(now), 'node': self.rpi_id, 'node_type': self.local_config['type'], 'log': 'Clear Videos'})
            self.publish_message('/logs/rpi/' + self.local_config['type'] +  '/' + str(self.rpi_id), blob)


