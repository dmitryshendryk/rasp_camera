import os
os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')

import time
import socket
import json
from datetime import datetime

import  threading
from threading import Thread

from utils import *
from config import Config
from mqtt_client import MQTTClient
from rpi import RPI
from camera import VideoGet
import time
import argparse


pid = os.getpid()
print('MQTT client starting with PID {}..'.format(pid))


def get_rpi_data(rpi_api, client, config):
    while True:
        blob = rpi_api.get_rpi_monitoring_data()
        blob['connectionStatus'] = True
        blob = json.dumps(blob)
        result, mid = client.publish_message('store/prishna/rpi/' + config._configuration_data['type'] + '/' + config._configuration_data['location'] + '/' + str(rpi_id), blob)
        print('event published: result={}, mid={}'.format(result, mid))


def monitor_rpi(rpi_api, client, config):
    t = Thread(target=get_rpi_data, args=(rpi_api, client, config))
    t.setDaemon(True)
    t.start()




if __name__ == "__main__":

    parser = argparse.ArgumentParser(
       description='RPIs')
    
    parser.add_argument('--device_type')

    args = parser.parse_args()

    while not internet():
        print('Waiting for internet connection')
        time.sleep(10)

    print('Connected to internet!')

    rpi_id = os.environ['RPI_ID']

    config = Config()
    print('Configuration')
    print(config._configuration_data)
    camera = VideoGet(rpi_config=config)
    client = MQTTClient(camera, rpi_config=config)
    rpi_api = RPI(rpi_config=config)
   
    client.mqttc.loop_start()

    monitor_rpi(rpi_api, client, config)
    is_movement = False 
    ## options to start as slave or master 
    if args.device_type == 'master':
        print('Start RPI as Master')
    elif args.device_type == 'slave':
        print('Start RPI as Slave')

    while True:

        if config._configuration_data['type'] == 'master':
            if not camera.is_recording:

                camera.is_movement = camera.get_movement()

            if camera.is_movement:
                camera.is_movement = False
                camera.start(client, is_timer=True)
                blob = json.dumps({'rpi_id': {'rpis': str(rpi_id), 'region': config._configuration_data['location']}, 'type': 'slave'})
                client.publish_message("store/prishna/rpi/actions/start_video", blob)
                