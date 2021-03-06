import unittest
import datetime
from unittest.mock import MagicMock

from osgar.drivers.lora import LoRa, parse_lora_packet, split_lora_buffer
from osgar.bus import BusHandler


class LoRaTest(unittest.TestCase):

    def test_parse_packet(self):
        addr, data = parse_lora_packet(b'4|alive\r\n')
        self.assertEqual(addr, [4])
        self.assertEqual(data, b'alive')
        addr, data = parse_lora_packet(b'4|1|2|pose(1, 2, 3)\r\n')
        self.assertEqual(addr, [4, 1, 2])
        self.assertEqual(data, b'pose(1, 2, 3)')

    def test_autodetect(self):
        SAMPLE_DATA = b'1|cmd=home\n'
        logger = MagicMock()
        robot_bus = BusHandler(logger, out={}, name='robot')
        bus = BusHandler(logger,
                         out={'raw':[(robot_bus.queue, 'raw')]},
                         name='lora')

        c = LoRa(bus=bus, config={'device_id': 4})
        c.start()
        c.bus.queue.put((123, 'raw', SAMPLE_DATA))
        c.request_stop()
        c.join()
        self.assertEqual(c.device_id, 4)

    def test_split_lora_buffer(self):
        self.assertEqual(split_lora_buffer(b'1|ble'), (b'1|ble', b''))
        self.assertEqual(split_lora_buffer(b'1|ble\n3|'), (b'3|', b'1|ble\n'))

    def test_invalid_packet(self):
        addr, data = parse_lora_packet(b'|pose(1, 2, 3)\r\n')
        self.assertIsNone(addr)
        self.assertEqual(data, b'|pose(1, 2, 3)\r\n')

    def test_autodetect_bug(self):
        logger = MagicMock()
        robot_bus = BusHandler(logger, out={}, name='robot')
        logger.write = MagicMock(return_value=datetime.timedelta(microseconds=9721))
        bus = BusHandler(logger,
                         out={'raw':[(robot_bus.queue, 'raw')]},
                         name='lora')

        c = LoRa(bus=bus, config={})  # force autodetection
        c.start()
        c.bus.queue.put((datetime.timedelta(microseconds=1331), 'raw', b'4|alive\n'))
#        c.bus.queue.put((datetime.timedelta(microseconds=29000), 'raw', b'4|alive-9721\n'))
        c.bus.queue.put((datetime.timedelta(microseconds=29000), 'raw', b'4|alive-97'))
        c.bus.queue.put((datetime.timedelta(microseconds=29200), 'raw', b'21\n'))
        c.request_stop()
        c.join()
        self.assertEqual(c.device_id, 4)

# vim: expandtab sw=4 ts=4
