from threading import Thread
import cv2
from datetime import datetime

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        

    def start(self):
        now = datetime.now()
        now_date = now.strftime("%d/%m/%Y_%H:%M:%S")
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        self.out = cv2.VideoWriter( now_date + '.avi', fourcc, 20.0, (640,480))
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                if self.grabbed:
                    self.out.write(self.frame)

    def stop(self):
        self.stopped = True

