from maya import cmds

from base import ModuleType
from ik_fk_limb import IkLimb, FkLimb

class Arm(IkLimb, FkLimb):

    COMPONENT_TYPE = ModuleType.ARM

    def __init__(self):
        IkLimb.__init__(self)
        FkLimb.__init__(self)
