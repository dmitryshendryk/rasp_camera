import  threading
from threading import Thread
import cv2
from datetime import datetime
import pathlib
# from config import Config
import os
from error import CameraNotConnected
import json
import imutils
import numpy as np
import time 
from datetime import datetime

rpi_id = os.environ['RPI_ID']




class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0, rpi_config=None):
        self.stream = cv2.VideoCapture(src)
        if self.stream is None or not self.stream.isOpened():
            raise CameraNotConnected()

        (self.grabbed, self.frame) = self.stream.read()
        # self.stopped = False
        self.stopped= threading.Event()
        self.config = rpi_config
        self.FRAMES_TO_PERSIST = 10

        self.MIN_SIZE_FOR_MOVEMENT = 2000

        self.MOVEMENT_DETECTED_PERSISTENCE = 100

        self.first_frame = None
        self.next_frame = None
        self.is_recording = False 
        self.is_movement = False
        self.enable_movement = True

        # Init display font and timeout counters
        # font = cv2.FONT_HERSHEY_SIMPLEX
        self.delay_counter = 0
        self.movement_persistent_counter = 0
        self.config._configuration_data = rpi_config._configuration_data


    def start(self, mqtt, is_timer):
        self.is_recording =True
        print('Start video recording')
        if self.stopped.is_set():
            self.stopped.clear()
        now = datetime.now()
        now_date = now.strftime("%d_%m_%Y__%H_%M_%S") ### change name  
        #### <timestamp>_<recordingdate>_<length_in_milliseconds>_<camera_id>_<camera_set_id>_<shop_id>_<compression>_<resolution>.m
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        video_save_path = './' + self.config._configuration_data['location'] + '/' + os.environ['RPI_ID']
        pathlib.Path(video_save_path).mkdir(parents=True, exist_ok=True) 
        # file_name = video_save_path + '/' + str(now_date) + '.avi'
        w, h = self.config._configuration_data['resolution']['w'], self.config._configuration_data['resolution']['h']

        file_name = video_save_path + '/' + str(int(time.time())) + '_' + str(now_date) + '_' + os.environ['RPI_ID'] + '_' + self.config._configuration_data['type'] + '_' + self.config._configuration_data['location'] + '_H264_' + str(w) +'_'+ str(h) + '.avi'
        self.out = cv2.VideoWriter(file_name, fourcc, 20.0, (w, h))
        t = Thread(target=self.get, args=(self.stopped, mqtt, is_timer))
        t.setDaemon(True)
        t.start()
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        blob = json.dumps({'time': str(now), 'node': str(rpi_id), 'node_type': self.config._configuration_data['type'], 'log': 'Start Recording Video'})
        mqtt.publish_message('/logs/rpi/' + self.config._configuration_data['type'] +  '/' + str(rpi_id), blob)
        
        return self

    
    def get_movement(self):
        if self.enable_movement:

            transient_movement_flag = False

            ret, frame = self.stream.read()
            text = "Unoccupied"

            # If there's an error in capturing
            if not ret:
                print("CAPTURE ERROR")

            frame = imutils.resize(frame, width = 750)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if self.first_frame is None: self.first_frame = gray    

            self.delay_counter += 1

            if self.delay_counter > self.FRAMES_TO_PERSIST:
                self.delay_counter = 0
                self.first_frame = self.next_frame

                
            self.next_frame = gray

            frame_delta = cv2.absdiff(self.first_frame, self.next_frame)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

            thresh = cv2.dilate(thresh, None, iterations = 2)
            _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in cnts:

                (x, y, w, h) = cv2.boundingRect(c)
                
                if cv2.contourArea(c) > self.MIN_SIZE_FOR_MOVEMENT:
                    transient_movement_flag = True
                    

            if transient_movement_flag == True:
                movement_persistent_flag = True
                self.movement_persistent_counter = self.MOVEMENT_DETECTED_PERSISTENCE

            if self.movement_persistent_counter > 0:
                text = "Movement Detected " + str(self.movement_persistent_counter)
                self.movement_persistent_counter -= 1
                return True
            else:
                text = "No Movement Detected"
                return False 
        else:
            print("Movement detection stopped")
            self.first_frame, self.next_frame = None, None 
            return False

    def get(self, stopped, mqtt, is_timer):
        blob = {}
        blob['connectionStatus'] = True
        blob = json.dumps(blob)
        
        start = time.time()
        while not stopped.is_set():
            if is_timer and (time.time() - start) > int(self.config._configuration_data['data']['record_threshold']):
                print("Timer Finished! Stop Camera!")
                self.stop(mqtt)

            if not self.grabbed:
                self.stop(mqtt)
            else:
                (self.grabbed, self.frame) = self.stream.read()
                if self.grabbed:
                    mqtt.mqttc.publish("/camera/recording/" + self.config._configuration_data['type'] +  '/' + self.config._configuration_data['location'] + '/' + str(rpi_id), blob)
                    self.out.write(self.frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

    def stop(self, mqtt):

        self.stopped.set()
        blob = {}
        blob['connectionStatus'] = False
        blob = json.dumps(blob)
        now = datetime.now()
        mqtt.mqttc.publish("/camera/recording/" + self.config._configuration_data['type'] +  '/' + self.config._configuration_data['location'] + '/' + str(rpi_id), blob)
        
        blob = json.dumps({'time': str(now), 'node': str(rpi_id), 'node_type': self.config._configuration_data['type'], 'log': 'Stop Recording Video'})
        mqtt.publish_message('/logs/rpi/' + self.config._configuration_data['type'] +  '/' +  self.config._configuration_data['location']+'/' + str(rpi_id), blob)
        
        self.is_recording = False
        
        
        # self.stopped = True
    def __del__(self):
        self.stream.release()
        cv2.destroyAllWindows()
        print("Camera disabled and all output windows closed...")


