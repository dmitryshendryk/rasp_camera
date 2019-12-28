import paho.mqtt.client as mqtt
from config import Config
import subprocess
import os 



class MQTTClient():

    def __init__(self):
        self.mqttc = mqtt.Client()
        self.mqttc.username_pw_set(Config.MQTT_USER, Config.MQTT_PASS)
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.connect(Config.MQTT_HOST, Config.MQTT_PORT, Config.MQTT_KEEP_ALIVE)
        self.mqttc.subscribe("store/prishna/rpi/actions/reboot", qos=1)

        self.mqttc.message_callback_add("store/prishna/rpi/actions/reboot", self.reboot_rpi)
    

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
        msg.payload = int(msg.payload)
        rpi_id = int(os.environ['RPI_ID'])
        if rpi_id == msg.payload:
            print('Reboot RPI {0}'.format(msg.payload))
            bashCommand = 'echo ' + os.environ['RPI_PASS'] + ' | sudo -S reboot'
            subprocess.call(bashCommand, shell=True)