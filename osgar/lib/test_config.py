import os
import unittest
from .config import *


def test_data(filename, test_dir='test_data'):
    return os.path.join(os.path.dirname(__file__), test_dir, filename)


class ConfigTest(unittest.TestCase):

    def test_empty_config(self):
        conf = Config()
        self.assertIsNone(conf.data.get('localization'))

    def test_load_config_files(self):
        conf_dir = '../../config'
        filename = test_data('ro2018-spider-gps-imu.json', conf_dir)
        conf = Config.load(filename)

    def test_multiple_config_files(self):
        conf_dir = '../../config'
        filename1 = test_data('ro2018-spider-gps-imu.json', conf_dir)
        filename2 = test_data('ro2018-czu-waypoints.json', conf_dir)
        conf = Config.load([filename1, filename2]).data
        self.assertIn('maxspeed',conf['robot']['modules']['app']['init'])
        self.assertIn('out',conf['robot']['modules']['app'])

    def test_merge_dict(self):
        self.assertEqual(Config.merge_dict({'A':1}, {'B':2}), {'A':1, 'B':2})

        dict1 = {'root':{'A':1}}
        dict2 = {'root':{'B':2}}
        merge = {'root':{'A':1, 'B':2}}
        self.assertEqual(Config.merge_dict(dict1, dict2), merge)

        self.assertEqual(Config.merge_dict({'A':1}, {'A':1}), {'A':1})

# vim: expandtab sw=4 ts=4

