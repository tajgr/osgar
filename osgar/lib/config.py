"""
  Osgar Config Class
"""
import json


class Config(object):

    OLD_SUPPORTED_VERSION = 1
    ROBOT_CONTAINER_VER = 2

    SUPPORTED_VERSIONS = [ROBOT_CONTAINER_VER]


    @classmethod
    def load(cls, filename):
        if isinstance(filename, list):
            filenames = filename
        else:
            filenames = [filename]
        
        ret = Config()
        for filename in filenames:
            with open(filename) as f:
                c = cls.loads(f.read())
                if ret is None:
                    ret.data = c.copy()
                else:
                    ret.data = Config.merge_dict(ret.data, c.data)
        return ret

    @classmethod
    def loads(cls, text_data):
        cls.data = json.loads(text_data)
        assert 'version' in cls.data, cls.data
        assert cls.data['version'] in cls.SUPPORTED_VERSIONS, cls.data['version']
        cls.version = cls.data['version']

        return cls

    @staticmethod
    def merge_dict(dict1, dict2):
        ret = dict1.copy()
        for key in dict2.keys():
            if key in dict1:
                if dict1[key] != dict2[key]:
                    ret[key] = Config.merge_dict(dict1[key], dict2[key])
            else:
                ret[key] = dict2[key]
        return ret

    def __init__(self):
        self.data = {}

# vim: expandtab sw=4 ts=4
