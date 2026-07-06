"""

Building a Config object for auto rigs module creation.

A Config object can be created with a dictionary such as a yaml file.

A Config object stores every useful information to customize modules for auto rig.

"""
import copy


class Config(object):
    """
    A Config Object can receive custom parameters (as dict) at initialization
    It modifies the self._datas dict that component must take their custom attributes from :
    e.g : self.COLOR will look for its value in self._datas[COLOR] dict

    The Config is given to an instance of BaseComponent to override their parameters and customize them
    e.g : BaseComponent instance had a self.COLOR="red" that has been overridden by Config to self.COLOR="blue"
    """

    HEADER = "CONFIG"

    def __init__(self, *args, **kwargs):
        self._datas = {}

        if args:
            for a in args:
                if isinstance(object, Config):
                    self._datas.update(a._datas)
                elif isinstance(a, dict):
                    self._datas.update(**a)
        if kwargs:
            self._datas.update(kwargs)

    def __getattr__(self, attr):
        """
        If the attribute you look for is a configurable parameter, fetch it into _datas dictionary
        """
        if attr.isupper():
            return self._datas[attr]
        else:
            return super().__getattr__(attr)

    def __str__(self):
        """
        Print the Config object as a structured string
        Taken from Simon Legrand's given code
        """
        out = "_" * 120 + "\n" + self.HEADER
        out += "\n" + '-' * 120 + "\n"
        if self._datas:
            longest_k = max([len(str(k)) for k in self._datas.keys()])
            for k, v in self._datas.items():
                out += f"\t{k}:  {(longest_k - len(str(k))) * ' '}{v}\n"
        else:
            out += " - - EMPTY - - \n"
        out += '_' * 120

        return out

    def __add__(self, other):
        """
        When adding a Config to another config or a dictionary,
        It creates another config with the current keys and updates them with the other keys
        Overrides keys if they already exists
        By creating a copy, you avoid modifying a Config which could be used in another Component
        """
        if isinstance(other, Config):
            config = copy.deepcopy(self)
            config._datas.update(other._datas)
            # self._datas.update(other.datas)
        elif isinstance(other, dict):
            config = copy.deepcopy(self)
            config._datas.update(**other)
            # self._datas.update(**other)
        return config

    def get(self, key : str, default = None):
        """
        Used when a Configuration requires to first get the value of a key,
        Then applying an operation to it
        """
        return self._datas.get(key, default)

    def set(self, key : str, value):
        """
        Used when you want to manually override a Config's key,
        """
        self._datas[key] = value

    @property
    def datas(self) -> dict:
        return self._datas

if __name__ == '__main__':
    custom_datas_dict = {
        "COLOR" : "pink",
        "PREFIX" : "rig_",
        "NAME_SPACE" : "ROBOT:",
        "USELESS_ATTR" : "USELESS",
        "MAMASITA" : 67,
    }


