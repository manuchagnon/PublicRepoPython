from maya import cmds

from enum import Enum, auto


class ComponentType(Enum):
    NONE = auto()
    SIMPLE = auto()
    CONTROLLER = auto()
    RIBBON = auto()

class BaseComponent:

    NAME_SPACE = None
    TYPE = ComponentType.NONE
    SIDE_SUFFIXES = ["_L", "_R"]
    JOINT_ORIENT = "X"
    GROUP_SUFFIX = "_grp"
    LOCATOR_PREFIX = "lct_"

    def __init__(self, name: str = None):

        cmds.select(clear=True)

        if name == None:
            self._name = ""
            self._side = ""
        else:
            side = ""
            for suffix in self.SIDE_SUFFIXES:
                if suffix in name:
                    side = suffix
                    name, side = name.rsplit(side, 1)
            self._name = name
            self._side = side

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # -- Name

    @property
    def name(self):
        return self._name + self.side_suffix

    @name.setter
    def name(self, name):
        old_name = self.name
        self._name = name
        cmds.rename(old_name, self.name)

    # -- Type

    @property
    def type(self):
        return self.TYPE

    # -- Side

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


if __name__ == '__main__':
    component = BaseComponent("test")
    print("nom =",component.name)
    component.side_suffix = "L"
    print("true size =", component.side_suffix)
    print("nom =",component.name)


    print("-")

    component = BaseComponent("test_side_02_L")
    print("nom =", component.name)
    print("true size =", component.side_suffix)

    print("-")

    component = BaseComponent("test_side_02_X")
    print("nom =", component.name)
    print("true size =", component.side_suffix)
