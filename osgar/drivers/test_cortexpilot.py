import unittest

from osgar.drivers.cortexpilot import Cortexpilot
from osgar.bus import BusHandler


class EduroTest(unittest.TestCase):

    def Xtest_usage(self):
        q = MagicMock()
        logger = MagicMock()
        logger.write = MagicMock(return_value=135)
        bus = BusHandler(logger=logger,
                out={'can': [], 'encoders': [], 'emergency_stop': [],
                     'pose2d': [(q, 'pose2d'),], 'buttons': []})
        eduro = Eduro(config={}, bus=bus)
        sync = CAN_packet(0x80, [])
        bus.queue.put((123, 'can', sync))
        bus.shutdown()
        eduro.run()
        q.put.assert_called_once_with((135, 'pose2d', [0, 0, 0]))

    def test_create_packet(self):
        robot = Cortexpilot(config={}, bus=None)
        packet = robot.create_packet()
        self.assertEqual(len(packet), 3 + 15)
        self.assertEqual(sum(packet) % 256, 0)
        self.assertEqual(packet[-1], 0xa3)

# vim: expandtab sw=4 ts=4
