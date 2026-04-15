from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.component.limb import IkLimb, FkLimb, Limb, IkFkLimb
from devMaya.utils.api import lock_attributes
from ..component.controller import Controller


class IkFk(IkFkLimb, BaseModule):
    """
    A IkFkLimb module contains :
        - an IkLimb module
        - an FkLimb module
        - a joint chain that blends between ik and fk joint chain
        - a switch ctl
    """
    TYPE = ModuleType.IK_FK_LIMB

    def __init__(self, jnt_list: list[str], name=None):
        IkFkLimb.__init__(self, jnt_list=jnt_list, name=name)

        self.set_input_and_output()
        self.arrange_nodes()


    def _build_ik_fk(self, jnt_list: list[str]):
        self.switch_ctl = Controller(jnt_list[0] + self.SWITCH_SUFFIX)
        pos = cmds.xform(jnt_list[0], q=1, ws=1, t=1)
        self.switch_ctl.pos = [pos[0], pos[1] + 2, pos[2]]
        self.switch_ctl.shape = self.CTL_SHAPE
        self.switch_ctl.color = self.CTL_COLOR
        cmds.rotate(0, 0, 90, self.switch_ctl.cvs, os=1, r=1)
        self._ctl_chain = [self.switch_ctl]

        lock_attributes(self.switch_ctl.name, attr_name="all")
        cmds.addAttr(self.switch_ctl.name, ln="switch_IK_FK", at="float", keyable=1, min=0, max=1, dv=0)

        for joint_IK, joint_FK, joint_blend in zip(self.ik_limb.jnts, self.fk_limb.jnts, self.jnts):
            # create pair_blend
            pair_blend = cmds.createNode("pairBlend", name=f'{joint_blend}_pb')

            # connect rotates to pair_blend
            cmds.connectAttr(f'{joint_FK}.rotate', f'{pair_blend}.inRotate1')
            cmds.connectAttr(f'{joint_IK}.rotate', f'{pair_blend}.inRotate2')
            cmds.connectAttr(f'{pair_blend}.outRotate', f'{joint_blend}.rotate')

            # connect switch attribute to pair_blend weight
            cmds.connectAttr(f'{self.switch_ctl}.switch_IK_FK', f'{pair_blend}.weight')

        # connect switch attribute to visibility
        cmds.connectAttr(f'{self.switch_ctl}.switch_IK_FK', f'{self.ik_limb.ctl_grp_name}.visibility')

        self.reverse = cmds.createNode("reverse", name=f'{jnt_list[0]}_rev')
        cmds.connectAttr(f'{self.switch_ctl}.switch_IK_FK', f"{self.reverse}.inputX")
        cmds.connectAttr(f"{self.reverse}.outputX", f'{self.fk_limb.ctl_grp_name}.visibility')

        # set ik and fk joints visibility to 0
        cmds.setAttr(f'{self.ik_limb.jnt_grp}.visibility', 0)
        cmds.setAttr(f'{self.fk_limb.jnt_grp}.visibility', 0)

    def set_input_and_output(self):
        cmds.xform(self.input, ws=1, t=self.fk_limb.ctls[0].pos)
        cmds.xform(self.output, ws=1, t=self.fk_limb.ctls[-1].pos)

        # constraint to controllers
        # cst = cmds.parentConstraint(self.ik_limb.ctl, self.fk_limb.ctls[-1], self.output, mo=False)[0]
        # cmds.connectAttr(f"{self.switch_ctl}.switch_IK_FK", f"{cst}.target[0].targetWeight", f=1)
        # cmds.connectAttr(f"{self.reverse}.outputX", f"{cst}.target[1].targetWeight", f=1)

        #constraint to blend joint chain
        cmds.parentConstraint(self.jnts[-1], self.output, mo=False)


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




