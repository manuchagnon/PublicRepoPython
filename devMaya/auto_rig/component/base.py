from maya import cmds

from enum import Enum, auto

from devMaya.auto_rig.configs.config import Config


class ComponentType(Enum):
    NONE = auto()
    SIMPLE = auto()
    CONTROLLER = auto()
    RIBBON = auto()
    LIMB = auto()
    FK_LIMB = auto()
    IK_LIMB = auto()
    IK_FK_LIMB = auto()

    FEATHER = auto()


class BaseComponent(object):

    NAME_SPACE = None
    TYPE = ComponentType.NONE
    SIDE_SUFFIXES = ["_L", "_R"]
    JOINT_ORIENT = "X"
    JOINT_PREFIX = "jnt_"
    LOCATOR_PREFIX = "lct_"
    CURVE_PREFIX = "crv_"
    GROUP_SUFFIX = "_grp"
    SCALE = 1

    def __init__(self, name: str = None, config: Config = None):
        # Implement Config behavior
        self._datas = {}
        self._config = config
        self.configure(self._config)

        if not name:
            self._name = ""
            self._side = ""
        else:
            side = ""
            for suffix in self.SIDE_SUFFIXES:
                if suffix in name:
                    side = suffix
                    name = name.rsplit(suffix, 1)[0]
            self._name = name
            self._side = side

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __getattribute__(self, item):
        """
        Implement the behavior for looking inside self._datas when looking for configurable attr
        e.g : self.CTL_COLOR will look inside self._datas[CTL_COLOR] in priority of self.__dict__
        Can possibly be improved :
        - try except not good
        - i used try except to avoid looking inside a list many times and directly
        """
        if item.isupper(): # if item is a configurable attr
            try:
                value = self._datas[item]
                # if item in object.__getattribute__(self, "_datas").keys():
                #     value = self._datas[item]
                # else:
                #     value = object.__getattribute__(self, item)
            except AttributeError:
                value = object.__getattribute__(self, item)
            except KeyError:
                value = object.__getattribute__(self, item)

            return value
        else:
            return object.__getattribute__(self, item) # normal behavior

    #region -- Name

    @property
    def name(self):
        return self._name + self.side_suffix

    @name.setter
    def name(self, name):
        old_name = self.name
        self._name = name
        cmds.rename(old_name, self.name)
    #endregion
    #region -- Type

    @property
    def type(self):
        return self.TYPE
    #endregion
    #region -- Side

    @property
    def side_suffix(self):
        return self._side


    @side_suffix.setter
    def side_suffix(self, side):
        if side in self.SIDE_SUFFIXES:
            self._side = side
        elif side in [self.SIDE_SUFFIXES[0][-1],self.SIDE_SUFFIXES[1][-1]]:
            self._side = "_" + side
        else:
            # no size change
            return

    def opposite_side(self):
        if not self.side_suffix:
            return None

        # change this module side and rename
        side_list = self.SIDE_SUFFIXES.copy()
        side_list.pop(self.SIDE_SUFFIXES.index(self.side_suffix))
        new_size = side_list[0]
        return new_size
    #endregion
    #region -- Config
    @property
    def datas(self):
        return self._datas

    def configure(self, config: Config | None):
        """
        Build the _datas dict that the component will be referring to when looking for configurable attr
        e.g : self.CTL_COLOR will look inside self._datas[CTL_COLOR] in priority of self.__dict__
        Can possibly be improved !
        """
        for attr in dir(self):
            if attr.isupper() :
                self._datas[attr] = object.__getattribute__(self, attr)

        if isinstance(config, Config):
            for key, value in config.__dict__().items():
                if hasattr(self, key): # doesn't store attributes that aren't used inside this component
                    self._datas[key] = value

    #endregion