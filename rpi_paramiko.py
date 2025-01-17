from paramiko import Transport, SFTPClient
from config import Config
import paramiko 
import time
import errno
import logging
from io import StringIO
import os 
logging.basicConfig(format='%(levelname)s : %(message)s',
                    level=logging.INFO)
import json

class SftpClient:

    _connection = None

    def __init__(self):
        self.host = Config.MQTT_HOST
        self.port = Config.SSH_PORT
        self.username = Config.HOST_USERNAME

        self.create_connection(self.host, self.port,
                               self.username,  Config.SSH_KEY_PATH)

    @classmethod
    def create_connection(cls, host, port, username, keyfilepath):
        if keyfilepath is not None:
            f = open(keyfilepath,'r')
            s = f.read()
            keyfile = StringIO(s)
            # Get private key used to authenticate user.
            key = paramiko.RSAKey.from_private_key(keyfile)

        transport = Transport(sock=(host, port))
        transport.connect(username=username, pkey=key)
        cls._connection = SFTPClient.from_transport(transport)

    @staticmethod
    def uploading_info(uploaded_file_size, total_file_size):

        logging.info('uploaded_file_size : {} total_file_size : {}'.
                     format(uploaded_file_size, total_file_size))

    def upload(self, local_path, remote_path):

        self._connection.put(localpath=local_path,
                             remotepath=remote_path,
                             callback=self.uploading_info,
                             confirm=True)

    def file_exists(self, remote_path):

        try:
            print('remote path : ', remote_path)
            self._connection.stat(remote_path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            raise
        else:
            return True

    def download(self, remote_path, local_path, retry=5):

        if self.file_exists(remote_path) or retry == 0:
            self._connection.get(remote_path, local_path,
                                 callback=None)
        elif retry > 0:
            time.sleep(5)
            retry = retry - 1
            self.download(remote_path, local_path, retry=retry)
    def close(self):
        self._connection.close()
    
    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            self._connection.mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise IOError
    def chdir(self, path):
        try:
            self._connection.chdir(path)
        except IOError:
            raise 

    def put_dir(self, source, target, mqtt):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are 
            created under target.
        '''
        blob = {}
        blob['connectionStatus'] = True
        for item in os.listdir(source):
            blob['connectionStatus'] = True
            mqtt.publish_message("/camera/uploading/" + mqtt.local_config['type'] +  '/' + mqtt.local_config['location'] + '/' + mqtt.rpi_id, json.dumps(blob))

            if os.path.isfile(os.path.join(source, item)):
                self._connection.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self._connection.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self._connection.put_dir(os.path.join(source, item), '%s/%s' % (target, item))
            
            blob['connectionStatus'] = False
            mqtt.publish_message("/camera/uploading/" + mqtt.local_config['type'] +  '/' + mqtt.local_config['location'] + '/' + mqtt.rpi_id, json.dumps(blob))

# ssh_client = SftpClient()