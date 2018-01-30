"""
  Spider3 Rider Driver
"""

import sys
import os
import inspect

OSGAR_ROOT = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if OSGAR_ROOT not in sys.path:
    sys.path.insert(0, OSGAR_ROOT) # access to logger without installation


import serial
from threading import Thread, Event

from lib.logger import LogWriter, LogReader


class Spider(Thread):
    def __init__(self, config, logger, output, name='spider'):
        Thread.__init__(self)
        self.setDaemon(True)
        self.should_run = Event()
        self.should_run.set()

        if 'port' in config:
            self.com = serial.Serial(config['port'], config['speed'])
            self.com.timeout = 0.01  # expects updates < 100Hz
        else:
            self.com = None
        self.logger = logger
        self.stream_id_in = config['stream_id_in']
        self.stream_id_out = config['stream_id_out']

        self.buf = b''
        self.output = output
        self.name = name

    @staticmethod
    def split_buffer(data):
        # TODO split data by CAN bridge packets
        assert False
        start = data.find(b'$')
        if start < 0:
            return data, b''
        end = data[start:-2].find(b'*')
        if end < 0:
            return data, b''
        return data[start+end+3:], data[start:start+end+3]

    def process(self, data):
        self.buf, line = self.split_buffer(self.buf + data)
        # TODO
        if line.startswith(b'$GNGGA') or line.startswith(b'$GPGGA'):
            coords = self.parse_line(line)
            if self.output:
                self.output(self.name, coords)
            return coords

    def run(self):
        while self.should_run.isSet():
            data = self.com.read(1024)
            if len(data) > 0:
                self.logger.write(self.stream_id, data)
                self.process(data)

    def request_stop(self):
        self.should_run.clear()


if __name__ == "__main__":
    pass

# vim: expandtab sw=4 ts=4
