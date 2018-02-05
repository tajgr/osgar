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
import struct
from threading import Thread, Event

from lib.logger import LogWriter, LogReader


CAN_BRIDGE_READY = b'\xfe\x10'  # CAN bridge is ready to accept configuration commands
CAN_BRIDGE_SYNC = b'\xFF'*10    # CAN bridge synchronization bytes
CAN_SPEED_1MB = b'\xfe\x57'     # configure CAN bridge to communicate on 1Mb CAN network
CAN_BRIDGE_START = b'\xfe\x31'  # start bridge


def CAN_packet(msg_id, data):
    header = [(msg_id>>3) & 0xff, (msg_id<<5) & 0xe0 | (len(data) & 0xf)]
    return bytes(header + data)


class Spider(Thread):
    def __init__(self, config, logger, output, name='spider'):
        Thread.__init__(self)
        self.setDaemon(True)
        self.should_run = Event()
        self.should_run.set()

        self.logger = logger
        self.stream_id_in = config['stream_id_in']
        self.stream_id_out = config['stream_id_out']

        self.buf = b''
        self.output = output
        self.name = name

        if 'port' in config:
            self.com = serial.Serial(config['port'], config['speed'], dsrdtr=1)
            self.com.setRTS()
            self.com.setDTR(0)
            self.com.timeout = 0.01  # expects updates < 100Hz
        else:
            self.com = None

        self.can_bridge_initialized = False
        self.status_word = None  # not defined yet
        self.wheel_angles = None  # four wheel angles as received via CAN
        self.zero_steering = None  # zero position of all 4 wheels
        self.speed_cmd = [0, 0]
        self.status_cmd = 3
        self.alive = 0  # toggle with 128

    @staticmethod
    def split_buffer(data):
        # skip 0xFF prefix bytes (CAN bridge control bytes)
        data = data.lstrip(b'\xff')

        if len(data) >= 2:
            # see https://en.wikipedia.org/wiki/CAN_bus
            header = data[:2]
            rtr = (header[1] >> 4) & 0x1  # Remote transmission request
            size = (header[1]) & 0x0f
            if rtr:
                return data[2:], header
            elif len(data) >= 2 + size:
                return data[2+size:], data[:2+size]
        return data, b''  # no complete packet available yet

    @staticmethod
    def fix_range(value):
        "into <-256, +256) interval"
        if value < -256:
            value += 512
        elif value >= 256:
            value -= 512
        return value

    def process(self, data, replay_only=False, verbose=False):
        self.buf, packet = self.split_buffer(self.buf + data)

        if packet == CAN_BRIDGE_READY and not replay_only:
            data = CAN_BRIDGE_SYNC
            self.logger.write(self.stream_id_out, data)
            self.com.write(data)
            data = CAN_SPEED_1MB
            self.logger.write(self.stream_id_out, data)
            self.com.write(data)
            data = CAN_BRIDGE_START
            self.logger.write(self.stream_id_out, data)
            self.com.write(data)
            self.can_bridge_initialized = True
            return None

        if len(packet) >= 2:
            msg_id = ((packet[0]) << 3) | (((packet[1]) >> 5) & 0x1f)
            if verbose:
                print(hex(msg_id), packet[2:])
            if msg_id == 0x200:
                self.status_word = struct.unpack('H', packet[2:])[0]

                if self.output:
                    self.output(self.name, self.status_word)
                return self.status_word
            elif msg_id == 0x201:
                assert len(packet) == 2 + 8, packet
                self.wheel_angles = struct.unpack_from('HHHH', packet, 2)
                if verbose and self.zero_steering is not None:
                    print('Wheels:',
                          [Spider.fix_range(a - b) for a, b in zip(self.wheel_angles, self.zero_steering)])
            elif msg_id == 0x203:
                assert len(packet) == 2 + 8, packet
                prev = self.zero_steering
                self.zero_steering = struct.unpack_from('HHHH', packet, 2)
                # make sure that calibration did not change during program run
                assert prev is None or prev == self.zero_steering, (prev, self.zero_steering)

    def run(self):
        while self.should_run.isSet():
            data = self.com.read(1024)
            if len(data) > 0:
                self.logger.write(self.stream_id_in, data)
                self.process(data)

    def request_stop(self):
        self.should_run.clear()

    def send(self, data):
        if self.can_bridge_initialized:
            speed, angular_speed = data
            if speed > 0:
                angle_cmd = int(angular_speed)  # TODO verify angle, byte resolution
                packet = CAN_packet(0x401, [0x80 + 127, angle_cmd])
            else:
                packet = CAN_packet(0x401, [0, 0])  # STOP packet
            self.logger.write(self.stream_id_out, packet)
            self.com.write(packet)

            # alive
            packet = CAN_packet(0x400, [self.status_cmd, self.alive])
            self.logger.write(self.stream_id_out, packet)
            self.com.write(packet)
            self.alive = 128 - self.alive
        else:
            print('CAN bridge not initialized yet!')
            self.logger.write(0, 'ERROR: CAN bridge not initialized yet! [%s]' % str(data))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parse Spider CAN packets')
    parser.add_argument('logfile', help='log filename')
    parser.add_argument('--stream', help='stream ID', type=int, default=None)
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
                        help='verbose output')
    args = parser.parse_args()

    # TODO read streams directly from log file configuration
    spider = Spider(config={'stream_id_in':1, 'stream_id_out':2}, logger=None, output=None)
    with LogReader(args.logfile) as log:
        for timestamp, stream_id, data in log.read_gen(args.stream):
            ret = spider.process(data, replay_only=True, verbose=args.verbose)
            if ret is not None:
                print(hex(ret))

# vim: expandtab sw=4 ts=4
