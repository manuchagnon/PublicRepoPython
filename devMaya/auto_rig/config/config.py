"""

Building a Config object for auto rigs module creation.

A Config object can be created from a nested dictionary such as a yaml file.

A Config object stores every useful information to customize modules for auto rig.

"""

# from yaml import load, dump

from devMaya.auto_rig.modules.base import BaseModule

class Config(object):

    def __init__(self, data: BaseModule | dict | None = None):

        self._data = {}

        if not data:
            return
        elif isinstance(data, dict):
            self._data = data
        elif isinstance(data, BaseModule):
            self.build_config_from_module(data)


    def __setattr__(self, key, value):
        self._data[key] = value

    def __getattr__(self, key):
        return self._data[key]

    def build_config_from_yaml(self):
        pass

    def build_config_from_dict(self, data):
        pass

    def build_config_from_module(self):
        pass



