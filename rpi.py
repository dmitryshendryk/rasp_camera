import psutil
import struct
import os
from gpiozero import CPUTemperature
from datetime import datetime
import time 







class RPI:

    def __init__(self):
        pass
        self.count = 0 
        self.upload=psutil.net_io_counters(pernic=True)['wlan0'][0]
        self.download=psutil.net_io_counters(pernic=True)['wlan0'][1]
        self.up_down=(self.upload,self.download)
        self.ul=0.00
        self.dl=0.00
        self.t0 = time.time()

    def get_rpi_monitoring_data(self):


        last_up_down = self.up_down
        self.upload=psutil.net_io_counters(pernic=True)['wlan0'][0]
        self.download=psutil.net_io_counters(pernic=True)['wlan0'][1]
        t1 = time.time()
        self.up_down = (self.upload,self.download)
        try:
            self.ul, self.dl = [(now - last) / (t1 - self.t0) / 1024.0
                    for now,last in zip(self.up_down, last_up_down)]             
            t0 = time.time()
        except:
            pass
        if self.dl>0.1 or self.ul>=0.1:
            time.sleep(0.25) 
        # print('UL: {:0.2f} kB/s \n'.format(ul)+'DL: {:0.2f} kB/s'.format(dl))

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
        
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        monitor = {'time': date_time, 'cpu_usage': cpu_usage, 'ram_percent_used': ram_percent_used, 'disk_percent_used': disk_percent_used,
                'cpu_temperature': cpu.temperature, 'ul': 'UL: {:0.2f} kB/s \n'.format(self.ul), 'dl': 'DL: {:0.2f} kB/s'.format(self.dl)}

        return monitor