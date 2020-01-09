import json

class Config:

    def __init__(self):
        try:
            with open("cfg/configuration.json", "r") as configuration_file:
                self._configuration_data = json.load(configuration_file)
        except FileNotFoundError as error:
            print(error)

    MQTT_HOST = '18.185.47.167'
    MQTT_PORT = 1883
    MQTT_KEEP_ALIVE = 60
    MQTT_PASS = '8Delusion-Serif'
    MQTT_USER = 'munich_broker'
    SSH_KEY_PATH = './s3_id_rsa'
    HOST_USERNAME = 'ubuntu'
    SSH_PORT = 2222