import unittest

from drivers.spider import Spider

class SpiderTest(unittest.TestCase):

    def test_split_buffer(self):
        self.assertEqual(Spider.split_buffer(b''), (b'', b''))
        self.assertEqual(Spider.split_buffer(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\x10'), (b'', b'\xfe\x10'))
        data = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfeW\xfe0@h\x9e\x01i\x01\xf7\x01\x18\x00'
        self.assertEqual(Spider.split_buffer(data), (b'\xfe0@h\x9e\x01i\x01\xf7\x01\x18\x00', b'\xfeW'))

        data = b'0@h\x9e\x01i\x01\xf7\x01\x18\x00'
        self.assertEqual(Spider.split_buffer(data), (b'h\x9e\x01i\x01\xf7\x01\x18\x00', b'0@'))

