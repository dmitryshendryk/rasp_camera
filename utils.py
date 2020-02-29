
import time
import socket
import json
import paramiko 

def internet(host="8.8.8.8", port=53, timeout=3):
  
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    print(ex)
    return False
