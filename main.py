import os
os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')

import time
import socket
import subprocess
import json
import socket
import time
from gpiozero import CPUTemperature



from datetime import datetime
from config import Config
from mqtt_client import MQTTClient
from rpi import RPI


pid = os.getpid()
print('MQTT client starting with PID {}..'.format(pid))


def internet(host="8.8.8.8", port=53, timeout=3):
  
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    print(ex)
    return False


if __name__ == "__main__":
        

    while not internet():
        print('Waiting for internet connection')
        time.sleep(10)

    print('Connected to internet!')

    rpi_id = os.environ['RPI_ID']

    client = MQTTClient()
    rpi_api = RPI()
   
    client.mqttc.loop_start()


    while True:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        blob = rpi_api.get_rpi_monitoring_data()
        blob['connectionStatus'] = True
        blob = json.dumps(blob)
        result, mid = client.publish_message('store/prishna/rpi/' + str(rpi_id), blob)
        print('event published: result={}, mid={}'.format(result, mid))

        time.sleep(1)
