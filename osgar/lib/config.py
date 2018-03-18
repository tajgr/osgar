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
        
        ret = None
        for filename in filenames:
            with open(filename) as f:
                c = cls.loads(f.read())
                if ret is None:
                    ret = c
                else:
                    ret.data.update(c.data)
        return ret

    @classmethod
    def loads(cls, text_data):
        cls.data = json.loads(text_data)
        assert 'version' in cls.data, cls.data
        assert cls.data['version'] in cls.SUPPORTED_VERSIONS, cls.data['version']
        cls.version = cls.data['version']

        return cls

    def __init__(self):
        self.data = {}

# vim: expandtab sw=4 ts=4
