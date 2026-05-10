from maya import cmds

from .base import BaseModule, ModuleType
from devMaya.auto_rig.component.controller import Controller

class Simple(BaseModule):

    TYPE = ModuleType.SIMPLE

    ROOT_SUFFIX = "_simple"

    CTL_COLOR = "green"
    CTL_SHAPE = "circle"

    def __init__(self, jnt : str=None, name=None):
        super().__init__(name=name)
        self._ctl_chain = []

        self._build_simple(jnt, name)
        self.set_input_and_output()
        self.arrange_nodes()

    def _build_simple(self, jnt, name):

        ctl_main = Controller(name + self.ROOT_SUFFIX)
        ctl_main.shape = self.CTL_SHAPE
        ctl_main.color = self.CTL_COLOR

        self._ctl_chain.append(ctl_main)

        # duplicate joint
        if not jnt:
            pos = [0, 0, 0]
            rot = [0, 0, 0]
        else:
            cmds.select(clear=True)
            pos = cmds.xform(jnt, q=1, ws=1, t=1)
            rot = cmds.xform(jnt, q=1, ws=1, ro=1)
        new_jnt = cmds.joint(name=jnt + self.ROOT_SUFFIX if jnt else "jnt" + self.ROOT_SUFFIX)
        self.jnt = new_jnt

        cmds.parent(new_jnt, self._ctl_chain[-1])

        cmds.xform(ctl_main.zro_grp_name, ws=1, t=pos, ro=rot)

    def set_input_and_output(self):
        cmds.xform(self.input, ws=1, t=self._ctl_chain[0].pos)
        cmds.xform(self.output, ws=1, t=self._ctl_chain[-1].pos)

        cmds.parentConstraint(self._ctl_chain[-1], self.output, mo=False)


    def arrange_nodes(self):
        obj_to_parent = [
            self._ctl_chain[0].zro_grp_name,
        ]
        super().arrange_nodes(obj_to_parent)