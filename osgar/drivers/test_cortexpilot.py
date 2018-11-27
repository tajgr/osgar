import unittest
from unittest.mock import MagicMock

from osgar.drivers.cortexpilot import Cortexpilot
from osgar.bus import BusHandler


class CortextpilotTest(unittest.TestCase):

    def test_usage(self):
        q = MagicMock()
        logger = MagicMock()
        logger.write = MagicMock(return_value=135)
        bus = BusHandler(logger=logger,
                out={'raw': [(q, 'raw')], 'encoders': [], 'emergency_stop': [],
                     'pose2d': [], 'buttons': []})
        robot = Cortexpilot(config={}, bus=bus)
        bus.queue.put((123, 'raw', b'sync'))
        robot.start()
        robot.request_stop()
        robot.join()
        q.put.assert_called_once_with((135, 'raw', 
            b'\x00\x00\x0f\x01\x0c\x00\x00\x00\x00\x00\x00\x00\x00A\x00\x00\x00\xa3'))

    def test_create_packet(self):
        robot = Cortexpilot(config={}, bus=None)
        packet = robot.create_packet()
        self.assertEqual(len(packet), 3 + 15)
        self.assertEqual(sum(packet) % 256, 0)
        self.assertEqual(packet[-1], 0xa3)

        robot.desired_speed = 0.5
        packet = robot.create_packet()
        self.assertEqual(len(packet), 3 + 15)
        self.assertEqual(sum(packet) % 256, 0)
        self.assertEqual(packet[-1], 0x64)

# vim: expandtab sw=4 ts=4
