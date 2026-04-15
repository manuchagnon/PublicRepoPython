from maya import cmds

from base import ModuleType
from ik_fk_limb import IkFkLimb

class Arm(IkFkLimb):

    TYPE = ModuleType.ARM
    CTL_COLOR = "blue"
    CTL_SHAPE = "double arrow"

    def __init__(self):
        super().__init__(self)
