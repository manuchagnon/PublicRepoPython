from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.component.limb import IkLimb, FkLimb, Limb, IkFkLimb
from devMaya.auto_rig.configs.config import Config
from devMaya.utils.api import lock_attributes, create_set
from ..component.controller import Controller

# class Fk(FkLimb, BaseModule):


class IkFk(BaseModule):
    """
    A IkFk module contains :
        - an IkFkLimb component
        - input and output locators
    """

    TYPE = ModuleType.IK_FK_LIMB

    BUILD_ROOT_CTL = True
    BUILD_BENDY = True
    BUILD_OFFSET_CTL = True
    BUILD_STRETCHY = True

    def __init__(self, jnt_list: list[str], name=None, config: Config=None):
        super().__init__(name, config=config)
        self.ik_fk_limb = IkFkLimb(jnt_list=jnt_list, name=name, config=config)

        if self.BUILD_ROOT_CTL:
            self.ik_fk_limb.build_root_ctl()
        if self.BUILD_BENDY:
            self.ik_fk_limb.build_bendy()
            cmds.parent(self.ik_fk_limb.ribbon.name, self.dont_touch_grp)
            cmds.parent(self.ik_fk_limb.ribbon.flc_grp_name, self.dont_touch_grp)
        elif self.BUILD_OFFSET_CTL:
            self.ik_fk_limb.build_offset_ctl()
        if self.BUILD_STRETCHY:
            self.ik_fk_limb.build_stretchy()

        # self.set_input_and_output()
        # self.arrange_nodes()

    def set_input_and_output(self):
        cmds.xform(self.input, ws=1, t=self.ik_fk_limb.fk_limb.ctls[0].pos)
        cmds.xform(self.output, ws=1, t=self.ik_fk_limb.fk_limb.ctls[-1].pos)

        # constraint to controllers
        # cst = cmds.parentConstraint(self.ik_limb.ctl, self.fk_limb.ctls[-1], self.output, mo=False)[0]
        # cmds.connectAttr(f"{self.switch_ctl}.switch_IK_FK", f"{cst}.target[0].targetWeight", f=1)
        # cmds.connectAttr(f"{self.reverse}.outputX", f"{cst}.target[1].targetWeight", f=1)

        #constraint to blend joint chain
        cmds.parentConstraint(self.ik_fk_limb.jnts[-1], self.output, mo=False)

    def arrange_nodes(self, obj_to_parent=[]):
        obj_to_parent += [
            self.ik_fk_limb.ctl_grp_name,

            self.ik_fk_limb.fk_limb.jnt_grp,

            self.ik_fk_limb.ik_limb.jnt_grp,
        ]

        # conditions if roots have been added in the limbs
        if not self.BUILD_ROOT_CTL:
            obj_to_parent += [
                self.ik_fk_limb.fk_limb.ctl_grp_name,
                self.ik_fk_limb.ik_limb.ctl_grp_name,
            ]

        if self.ik_fk_limb.jnt_grp: # if the joint chain has been duplicated
            obj_to_parent.append(self.ik_fk_limb.jnt_grp)

        super().arrange_nodes(obj_to_parent)

    # def mirror(self, axis=[-1, 1, 1]):
    #     super().mirror(axis=axis)

        # Flip the ribbon surface
        # not well implemented because if the module have several ribbons inside it, it is bad to it this way
        # if self.BUILD_BENDY:
        #     cmds.reverseSurface(self.ik_fk_limb.ribbon.name, d=1, ch=0, rpo=1)


    def bind_jnts(self):
        bind_jnts = self.ik_fk_limb.jnts
        create_set(bind_jnts, set_name="bind_jnts_set")
        return bind_jnts


