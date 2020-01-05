from paramiko import Transport, SFTPClient
from config import Config
import paramiko 
import time
import errno
import logging
logging.basicConfig(format='%(levelname)s : %(message)s',
                    level=logging.INFO)


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
            # Get private key used to authenticate user.
            key = paramiko.RSAKey.from_private_key(keyfilepath)

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



ssh_client = SftpClient()