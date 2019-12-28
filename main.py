from __future__ import division
from subprocess import PIPE, Popen
import psutil
import struct
import os
os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')

import time
import socket
import subprocess
import json
import socket
import time
from gpiozero import CPUTemperature



import paho.mqtt.client as mqtt
from datetime import datetime
from config import Config


pid = os.getpid()
print('MQTT client starting with PID {}..'.format(pid))


def internet(host="8.8.8.8", port=53, timeout=3):
  """
  Host: 8.8.8.8 (google-public-dns-a.google.com)
  OpenPort: 53/tcp
  Service: domain (DNS/TCP)
  """
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    print(ex)
    return False

def reboot_rpi(mqttc, obj, msg):
    msg.payload = int(msg.payload)
    rpi_id = int(os.environ['RPI_ID'])
    if rpi_id == msg.payload:
        print('Reboot RPI {0}'.format(msg.payload))
        bashCommand = 'echo ' + os.environ['RPI_PASS'] + ' | sudo -S reboot'
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output, error)




def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_command(mqttc, obj, msg):
    print('Command topics')
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))



def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

def get_rpi_monitoring_data():

    cpu_usage = psutil.cpu_percent()

    ram = psutil.virtual_memory()
    ram_total = ram.total / 2**20       # MiB.
    ram_used = ram.used / 2**20
    ram_free = ram.free / 2**20
    ram_percent_used = ram.percent

    disk = psutil.disk_usage('/')
    disk_total = disk.total / 2**30     # GiB.
    disk_used = disk.used / 2**30
    disk_free = disk.free / 2**30
    disk_percent_used = disk.percent
    cpu = CPUTemperature()

    monitor = {'cpu_usage': cpu_usage, 'ram_percent_used': ram_percent_used, 'disk_percent_used': disk_percent_used,
			'cpu_temperature': cpu.temperature}

    return monitor



if __name__ == "__main__":
        


    while not internet():
        print('Waiting for internet connection')
        time.sleep(10)

    print('Connected to internet!')

    rpi_id = os.environ['RPI_ID']

    mqttc = mqtt.Client()
    mqttc.username_pw_set("munich_broker", "8Delusion-Serif")
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    mqttc.connect(Config.MQTT_HOST, Config.MQTT_PORT, Config.MQTT_KEEP_ALIVE)
    mqttc.subscribe("store/prishna/rpi/actions/reboot", qos=1)

    mqttc.message_callback_add("store/prishna/rpi/actions/reboot", reboot_rpi)


    mqttc.loop_start()


    seq = 1
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    while True:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        blob = get_rpi_monitoring_data()
        blob['connectionStatus'] = True
        blob = json.dumps(blob)
        result, mid = mqttc.publish('store/prishna/rpi/' + str(rpi_id), blob, qos=0, retain=True)
        print('event published: result={}, mid={}'.format(result, mid))

        seq += 1
        time.sleep(1)
