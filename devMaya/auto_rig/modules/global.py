from maya import cmds

from .base import BaseModule, ModuleType
from devMaya.auto_rig.component.controller import Controller

class Global(BaseModule):

    TYPE = ModuleType.GLOBAL

    CTL_GLOBAL_SUFFIX = "_global"
    CTL_GLOBAL_COLOR = "green"
    CTL_GLOBAL_SHAPE = "global"

    CTL_OFFSET_SUFFIX = "_offset"
    CTL_OFFSET_COLOR = "yellow"
    CTL_OFFSET_SHAPE = "square"
    CTL_OFFSET_AMOUNT = 2

    def __init__(self, name=None):
        super().__init__(self, name = name)
        self._ctl_chain = []

        self._build_global(name)
        self.set_input_and_output()
        self.arrange_nodes(obj_to_parent=[])

    def build_global(self, name):
        self.ctl_main = Controller(name + self.CTL_GLOBAL_SUFFIX)
        self.ctl_main.shape = self.CTL_GLOBAL_SHAPE
        self.ctl_main.color = self.CTL_GLOBAL_COLOR
        self._ctl_chain.append(self.ctl_main)

        for i in range(self.CTL_OFFSET_AMOUNT):
            ctl = Controller(name + str(i) + self.CTL_OFFSET_SUFFIX)
            ctl.shape = self.CTL_OFFSET_SHAPE
            ctl.color = self.CTL_OFFSET_COLOR
            ctl.scale = 0.90 ** i

            cmds.parent(ctl, self._ctl_chain[i])
            self._ctl_chain.append(ctl)

    def set_input_and_output(self):
        pass

    def arrange_nodes(self):
        obj_to_parent = [
            self.ik_limb.jnt_grp,
            self.fk_limb.jnt_grp,

            self.fk_limb.ctl_grp_name,
            self.ik_limb.ctl_grp_name,

            self.jnt_grp,
            self.ctl.zro_grp_name,
        ]
        super().arrange_nodes(obj_to_parent)
