import  threading
from threading import Thread
import cv2
from datetime import datetime
import pathlib
from config import Config
import os
from error import CameraNotConnected


class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        if self.stream is None or not self.stream.isOpened():
            raise CameraNotConnected()

        (self.grabbed, self.frame) = self.stream.read()
        # self.stopped = False
        self.stopped= threading.Event()
        self.config = Config()

        



    def start(self):
        if self.stopped.is_set():
            self.stopped.clear()
        now = datetime.now()
        now_date = now.strftime("%d_%m_%Y__%H_%M_%S")
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        video_save_path = './' + self.config._configuration_data['location'] + '/' + os.environ['RPI_ID']
        pathlib.Path(video_save_path).mkdir(parents=True, exist_ok=True) 
        file_name = video_save_path + '/' + str(now_date) + '.avi'
        self.out = cv2.VideoWriter(file_name, fourcc, 20.0, (640,480))
        t = Thread(target=self.get, args=(self.stopped, ))
        t.setDaemon(True)
        t.start()
        return self

    def get(self, stopped):
        while not stopped.is_set():
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                if self.grabbed:
                    self.out.write(self.frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

    def stop(self):
        # self.stream.release()
        self.stopped.set()
        # self.stopped = True
    def __del__(self):
        self.stream.release()
        cv2.destroyAllWindows()
        print("Camera disabled and all output windows closed...")
