"""
  Wrapper for CAN-serial communication and control of CAN bridge
"""

import sys
import os
import inspect

# -------- remove with "osgar" package --------
OSGAR_ROOT = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if OSGAR_ROOT not in sys.path:
    sys.path.insert(0, OSGAR_ROOT) # access to logger without installation
# ------------- end ---------------

import serial
import struct
from threading import Thread

from lib.logger import LogWriter, LogReader
from drivers.bus import BusShutdownException


CAN_BRIDGE_READY = b'\xfe\x10'  # CAN bridge is ready to accept configuration commands
CAN_BRIDGE_SYNC = b'\xFF'*10    # CAN bridge synchronization bytes
CAN_SPEED_1MB = b'\xfe\x57'     # configure CAN bridge to communicate on 1Mb CAN network
CAN_BRIDGE_START = b'\xfe\x31'  # start bridge


def CAN_packet(msg_id, data):
    header = [(msg_id>>3) & 0xff, (msg_id<<5) & 0xe0 | (len(data) & 0xf)]
    return bytes(header + data)


class CANSerial(Thread):
    def __init__(self, config, bus):
        Thread.__init__(self)
        self.setDaemon(True)

        self.bus = bus
        self.buf = b''

        self.can_bridge_initialized = False

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

    def process_packet(self, packet, replay_only=False, verbose=False):
        if packet == CAN_BRIDGE_READY and not replay_only:
            self.bus.publish('raw', CAN_BRIDGE_SYNC)
            self.bus.publish('raw', CAN_SPEED_1MB)
            self.bus.publish('raw', CAN_BRIDGE_START)
            self.can_bridge_initialized = True
            return None

        if len(packet) >= 2:
            msg_id = ((packet[0]) << 3) | (((packet[1]) >> 5) & 0x1f)
            if verbose:
                print(hex(msg_id), packet[2:])

    def process_gen(self, data, replay_only=False, verbose=False):
        self.buf, packet = self.split_buffer(self.buf + data)
        while len(packet) > 0:
            ret = self.process_packet(packet, replay_only=replay_only, verbose=replay_only)
            if ret is not None:
                yield ret
            self.buf, packet = self.split_buffer(self.buf)  # i.e. process only existing buffer now

    def run(self):
        try:
            while True:
                dt, channel, data = self.bus.listen()
                if len(data) > 0:
                    for __ in self.process_gen(data):
                        pass
        except BusShutdownException:
            pass

    def request_stop(self):
        self.bus.shutdown()

    def send(self, data):
        if self.can_bridge_initialized:
            pass
        else:
            print('CAN bridge not initialized yet!')
#            self.logger.write(0, 'ERROR: CAN bridge not initialized yet! [%s]' % str(data))


if __name__ == "__main__":
    pass


# vim: expandtab sw=4 ts=4
