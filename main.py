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


pid = os.getpid()
print('MQTT client starting with PID {}..'.format(pid))


def get_rpi_data(rpi_api, client):
    blob = rpi_api.get_rpi_monitoring_data()
    blob['connectionStatus'] = True
    blob = json.dumps(blob)
    result, mid = client.publish_message('store/prishna/rpi/' + config['type'] + '/' + str(rpi_id), blob)
    print('event published: result={}, mid={}'.format(result, mid))
    time.sleep(1)


def monitor_rpi(rpi_api, client):
    t = Thread(target=get_rpi_data, args=(rpi_api, client))
    t.setDaemon(True)
    t.start()




if __name__ == "__main__":
        

    while not internet():
        print('Waiting for internet connection')
        time.sleep(10)

    print('Connected to internet!')

    rpi_id = os.environ['RPI_ID']

    with open('./cfg/configuration.json', 'r') as f:
        config = json.load(f)

    client = MQTTClient()
    rpi_api = RPI()
   
    client.mqttc.loop_start()


    while True:

        monitor_rpi(rpi_api, client)
        # blob = rpi_api.get_rpi_monitoring_data()
        # blob['connectionStatus'] = True
        # blob = json.dumps(blob)
        # result, mid = client.publish_message('store/prishna/rpi/' + config['type'] + '/' + str(rpi_id), blob)
        # print('event published: result={}, mid={}'.format(result, mid))

