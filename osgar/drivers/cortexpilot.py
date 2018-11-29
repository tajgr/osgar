"""
  Driver for robot Robik from cortexpilot.com
"""

import struct
from threading import Thread

from osgar.bus import BusShutdownException


class Cortexpilot(Thread):
    def __init__(self, config, bus):
        Thread.__init__(self)
        self.setDaemon(True)

        self.bus = bus
        self._buf = b''

        # commands
        self.desired_speed = 0.0  # m/s
        self.desired_angular_speed = 0.0
        self.cmd_flags = 0x41  # local steering, PWM OFF, laser ON, TODO

        # status
        self.emergency_stop = None  # uknown state
        self.pose = (0.0, 0.0, 0.0)  # x, y in meters, heading in radians (not corrected to 2PI)
        self.flags = None
        self.voltage = None
        self.last_encoders = None

    def create_packet(self):
        packet = struct.pack('<ffI', self.desired_speed,
                             self.desired_angular_speed, self.cmd_flags)
        assert len(packet) < 256, len(packet)  # just to use LSB only
        ret = bytes([0, 0, len(packet) + 2 + 1, 0x1, 0x0C]) + packet
        checksum = sum(ret) & 0xFF
        return ret + bytes([256-checksum])

    def get_packet(self):
        """extract packet from internal buffer (if available otherwise return None"""
        data = self._buf
        if len(data) < 5:
            return None
        high, mid, low = data[:3]  # packet length
        assert high == 0, high  # all messages < 65535 bytes
        size = 256 * mid + low + 3  # counting also 3 bytes of len header
        if len(data) < size:
            return None
        ret, self._buf = data[:size], data[size:]
        checksum = sum(ret) & 0xFF
        assert checksum == 0, checksum  # checksum error
        return ret

    def parse_packet(self, data):
        # expects already validated single sample with 3 bytes length prefix
        addr = data[3]
        assert addr == 1, addr
        cmd = data[4]
        assert cmd in [0x1, 0xC], cmd
        self.flags, self.voltage = struct.unpack_from('<If', data, 5)
        encoders = struct.unpack_from('<II', data, 5 + 6 * 4)
        if self.last_encoders is not None:
            step = [x - prev for x, prev in zip(encoders, self.last_encoders)]
            self.bus.publish('encoders', step)
        self.last_encoders = encoders

    def run(self):
        try:
            self.bus.publish('raw', self.create_packet())
            while True:
                dt, channel, data = self.bus.listen()
                if channel == 'raw':
                    self._buf += data
                    packet = self.get_packet()
                    if packet is not None:
                        self.parse_packet(packet)
                        self.bus.publish('raw', self.create_packet())

        except BusShutdownException:
            pass

    def request_stop(self):
        self.bus.shutdown()

# vim: expandtab sw=4 ts=4
