import psutil
import struct
import os
from gpiozero import CPUTemperature

class RPI:

    def __init__(self):
        pass


    def get_rpi_monitoring_data(self):

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

        monitor = {'cpu_usage': cpu_usage, 'ram_percent_used': ram_percent_used, 'disk_percent_used': disk_percent_used,
                'cpu_temperature': cpu.temperature}

        return monitor