"""

Building a Config object for auto rigs module creation.

A Config object can be created with a dictionary such as a yaml file.

A Config object stores every useful information to customize modules for auto rig.

"""

class Config:
    """
    A Config Object can receive custom parameters (as dict) at initialization
    It modifies the self._datas dict that component must take their attributes from :
    e.g : self.COLOR will look for its value in self._datas[COLOR] dict

    The Config is given to an instance of BaseComponent to override their parameters and customize them
    e.g : BaseComponent instance had a self.COLOR that has been overridden by Config
    """

    HEADER = "CONFIG"

    def __init__(self, *args, **kwargs):
        self._datas = {}

        if args:
            for a in args:
                if type(a) is dict:
                    self.__dict__().update(a)
                # elif type(a) is type(self):
                #     self.__dict__.update(a.__dict__)

        self.__dict__().update(kwargs)

    def __dict__(self):
        return self._datas

    def __getattr__(self, attr):
        return self._datas[attr]

    def __str__(self):
        """
        Taken from Simon Legrand's code
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
        if isinstance(object, Config):
            self.__dict__().update(other.__dict__())
            return self
        elif isinstance(other, dict):
            self.__dict__().update(**other)
            return self
        else:
            return self

if __name__ == '__main__':
    custom_datas_dict = {
        "COLOR" : "pink",
        "PREFIX" : "rig_",
        "NAME_SPACE" : "ROBOT:",
        "USELESS_ATTR" : "USELESS",
        "MAMASITA" : 67,
    }

    my_config = Config(custom_datas_dict)

