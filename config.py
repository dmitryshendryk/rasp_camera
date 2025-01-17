import json

class Config:

    def __init__(self):
        try:
            with open("cfg/configuration.json", "r") as configuration_file:
                self._configuration_data = json.load(configuration_file)
        except FileNotFoundError as error:
            print(error)
        
    def set_config(self, json):
        self._configuration_data['data'] = json

    MQTT_HOST = '52.59.124.185'
    MQTT_PORT = 1883
    MQTT_KEEP_ALIVE = 60
    MQTT_PASS = '8Delusion-Serif'
    MQTT_USER = 'munich_broker'
    SSH_KEY_PATH = './s3_id_rsa'
    HOST_USERNAME = 'ubuntu'
    SSH_PORT = 2222
    aws_access_key_id='AKIAU5EBQB3PL4TG6IJL'
    aws_secret_access_key='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'
    s3_bucket_name = 'openlens-production'