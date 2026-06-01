from maya import cmds

from .base import BaseModule, ModuleType
from devMaya.auto_rig.modules.simple import Simple
from devMaya.auto_rig.component.controller import Controller

class Root(BaseModule):

    TYPE = ModuleType.ROOT

    ROOT_SUFFIX = "_root"

    CTL_ROOT_COLOR = "green"
    CTL_ROOT_SHAPE = "root"

    CTL_OFFSET_SUFFIX = "_offset"
    CTL_OFFSET_COLOR = "yellow"
    CTL_OFFSET_SHAPE = "circle"
    CTL_OFFSET_AMOUNT = 2

    def __init__(self, jnt : str=None, name=None):
        super().__init__(name=name)

        self._build_root(jnt, name)
        self.set_input_and_output()
        self.arrange_nodes()

    def _build_root(self, jnt, name):

        ctl_main = Controller(name + self.ROOT_SUFFIX)
        ctl_main.shape = self.CTL_ROOT_SHAPE
        ctl_main.color = self.CTL_ROOT_COLOR
        ctl_main.shape_scale = 0.9

        self._ctl_chain.append(ctl_main)

        for i in range(self.CTL_OFFSET_AMOUNT):
            ctl = Controller(name + str(i) + self.CTL_OFFSET_SUFFIX)
            ctl.shape = self.CTL_OFFSET_SHAPE
            ctl.color = self.CTL_OFFSET_COLOR
            ctl.shape_scale = 0.90 ** i

            cmds.parent(ctl.zro_grp_name, self._ctl_chain[i])
            self._ctl_chain.append(ctl)

        # duplicate joint
        if not jnt:
            pos = [0, 0, 0]
            rot = [0, 0, 0]
        else:
            cmds.select(clear=True)
            pos = cmds.xform(jnt, q=1, ws=1, t=1)
            rot = cmds.xform(jnt, q=1, ws=1, ro=1)
        new_jnt = cmds.joint(name = jnt + self.ROOT_SUFFIX if jnt else "jnt" + self.ROOT_SUFFIX)
        self.jnt = new_jnt

        cmds.parent(new_jnt, self._ctl_chain[-1])

        cmds.xform(ctl_main.zro_grp_name, ws=1, t=pos, ro=rot)


    def set_input_and_output(self):
        cmds.xform(self.input, ws=1, t=self._ctl_chain[0].pos)
        cmds.xform(self.output, ws=1, t=self._ctl_chain[-1].pos)

        # cmds.parentConstraint(self._ctl_chain[-1], self.output, mo=False)
        cmds.parent(self.output, self._ctl_chain[-1])




    def arrange_nodes(self):
        obj_to_parent = [
            self._ctl_chain[0].zro_grp_name,
        ]
        super().arrange_nodes(obj_to_parent)

class Root(Simple):

    TYPE = ModuleType.ROOT

    ROOT_SUFFIX = "_root"

    CTL_ROOT_COLOR = "green"
    CTL_ROOT_SHAPE = "root"

    CTL_OFFSET_SUFFIX = "_offset"
    CTL_OFFSET_COLOR = "yellow"
    CTL_OFFSET_SHAPE = "circle"
    CTL_OFFSET_AMOUNT = 2

    def __init__(self, jnt : str=None, name=None):
        super().__init__(name=name)

        self._build_root(jnt, name)
        self.set_input_and_output()
        self.arrange_nodes()

    def _build_root(self, jnt, name):

        ctl_main = Controller(name + self.ROOT_SUFFIX)
        ctl_main.shape = self.CTL_ROOT_SHAPE
        ctl_main.color = self.CTL_ROOT_COLOR
        ctl_main.shape_scale = 0.9

        self._ctl_chain.append(ctl_main)

        for i in range(self.CTL_OFFSET_AMOUNT):
            ctl = Controller(name + str(i) + self.CTL_OFFSET_SUFFIX)
            ctl.shape = self.CTL_OFFSET_SHAPE
            ctl.color = self.CTL_OFFSET_COLOR
            ctl.shape_scale = 0.90 ** i

            cmds.parent(ctl.zro_grp_name, self._ctl_chain[i])
            self._ctl_chain.append(ctl)

        # duplicate joint
        if not jnt:
            pos = [0, 0, 0]
            rot = [0, 0, 0]
        else:
            cmds.select(clear=True)
            pos = cmds.xform(jnt, q=1, ws=1, t=1)
            rot = cmds.xform(jnt, q=1, ws=1, ro=1)
        new_jnt = cmds.joint(name = jnt + self.ROOT_SUFFIX if jnt else "jnt" + self.ROOT_SUFFIX)
        self.jnt = new_jnt

        cmds.parent(new_jnt, self._ctl_chain[-1])

        cmds.xform(ctl_main.zro_grp_name, ws=1, t=pos, ro=rot)


    def set_input_and_output(self):
        cmds.xform(self.input, ws=1, t=self._ctl_chain[0].pos)
        cmds.xform(self.output, ws=1, t=self._ctl_chain[-1].pos)

        # cmds.parentConstraint(self._ctl_chain[-1], self.output, mo=False)
        cmds.parent(self.output, self._ctl_chain[-1])




    def arrange_nodes(self):
        obj_to_parent = [
            self._ctl_chain[0].zro_grp_name,
        ]
        super().arrange_nodes(obj_to_parent)