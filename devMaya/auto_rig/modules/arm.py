from devMaya.auto_rig.modules.base import ModuleType
from devMaya.auto_rig.modules.ik_fk import IkFk
from devMaya.auto_rig.configs.config import Config

class Arm(IkFk):

    TYPE = ModuleType.ARM

    BUILD_ROOT_CTL : bool = True
    BUILD_BENDY : bool = True
    BUILD_OFFSET_CTL : bool = True
    BUILD_STRETCHY : bool = True

    IK_FK_SWITCH : int | bool = 0

    def __init__(self, jnt_list: list[str], name=None, config: Config = None):
        super().__init__(jnt_list=jnt_list, name=name, config=config)