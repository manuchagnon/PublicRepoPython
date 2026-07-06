from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
# from devMaya.auto_rig.modules.foot import Feet circular importation
from devMaya.auto_rig.component.limb import IkLimb, FkLimb, Limb, IkFkLimb
from devMaya.auto_rig.configs.config import Config
from devMaya.utils.api import (lock_attributes, create_set, replace_in_names, Attribute)
from ..component.controller import Controller

class Fk(BaseModule):

    TYPE = ModuleType.FK_LIMB

    BUILD_ROOT_CTL : bool = True
    BUILD_BENDY : bool = True
    BUILD_OFFSET_CTL : bool = True
    BUILD_MAINTAIN_VOLUME : bool = False

    HINGE_SUFFIX : str = "_hinge"

    def __init__(self, jnt_list : list[str], name = None, config : Config = None):
        super().__init__(name, config=config)
        self.fk_limb = FkLimb(jnt_list=jnt_list, name=name, config=config)
        # cmds.parent(self.ik_fk_limb.ik_handle(), self.dont_touch_grp)

        if self.BUILD_ROOT_CTL:
            self.fk_limb.build_root_ctl()
        if self.BUILD_BENDY:
            self.fk_limb.build_bendy()
            cmds.parent(self.fk_limb.ribbon.name, self.dont_touch_grp)
            cmds.parent(self.fk_limb.ribbon.flc_grp_name, self.dont_touch_grp)
            if self.BUILD_MAINTAIN_VOLUME:
                self.fk_limb.build_maintain_volume_setup()
        elif self.BUILD_OFFSET_CTL:
            self.fk_limb.build_offset_ctl()

    def set_input_and_output(self, input : str =None, output : str = None, input_pos=None, output_pos=None):
        super().set_input_and_output(input=self.fk_limb.ctls[0], output=self.fk_limb.ctls[-1], input_pos=input_pos, output_pos=output_pos)

        # cmds.xform(self.input, ws=1, t=self.fk_limb.ctls[0].pos)
        # cmds.xform(self.output, ws=1, t=self.fk_limb.ctls[-1].pos)
        #
        # cmds.parentConstraint(self.fk_limb.jnts[-1], self.output, mo=False)

    def arrange_nodes(self, obj_to_parent=[]):
        obj_to_parent += [
            self.fk_limb.ctl_grp_name,
            self.fk_limb.jnt_grp,
        ]

        super().arrange_nodes(obj_to_parent)

    def bind_jnts(self, bind_jnts : list[str] = []) -> list[str]:
        bind_jnts += self.fk_limb.bind_jnts()
        return super().bind_jnts(bind_jnts=bind_jnts)

class IkFk(BaseModule):
    """
    A IkFk module contains :
        - an IkFkLimb component
        - input and output locators
    """

    TYPE = ModuleType.IK_FK_LIMB

    BUILD_ROOT_CTL : bool = True
    BUILD_BENDY : bool = True
    BUILD_LOCK_ELBOW : bool = True
    BUILD_OFFSET_CTL : bool = True
    BUILD_STRETCHY : bool = True
    BUILD_MAINTAIN_VOLUME : bool = False

    IK_FK_SWITCH : int | bool = 0

    HINGE_SUFFIX : str = "_hinge"

    CTL_IK_PARENTS_NAME : list[str] = ["normal"]
    CTL_POLE_PARENTS_NAME : list[str] = ["normal", "hand"]

    def __init__(self, jnt_list: list[str], name=None, config: Config=None):
        super().__init__(name=name, config=config)
        self.ik_fk_limb = IkFkLimb(jnt_list=jnt_list, name=name, config=config)
        self.ik_fk_limb.set_ik_fk_switch(self.IK_FK_SWITCH)

        # cmds.parent(self.ik_fk_limb.ik_handle(), self.dont_touch_grp)

        if self.BUILD_ROOT_CTL:
            self.ik_fk_limb.build_root_ctl()
        if self.BUILD_BENDY:
            self.ik_fk_limb.build_bendy()
            cmds.parent(self.ik_fk_limb.ribbon.name, self.dont_touch_grp)
            cmds.parent(self.ik_fk_limb.ribbon.flc_grp_name, self.dont_touch_grp)
            if self.BUILD_LOCK_ELBOW:
                self.ik_fk_limb.build_lock_elbow()
            if self.BUILD_MAINTAIN_VOLUME:
                self.ik_fk_limb.build_maintain_volume_setup()
        elif self.BUILD_OFFSET_CTL:
            self.ik_fk_limb.build_offset_ctl()
        if self.BUILD_STRETCHY:
            self.ik_fk_limb.build_stretchy()


        # self.set_input_and_output()
        # self.arrange_nodes()

    def ik_handle(self):
        return self.ik_fk_limb.ik_handle()

    def toggle_if_fk(self):
        """
        Switch between fk and ik state with the API
        """
        self.ik_fk_limb.toggle_if_fk()

    def build_switch_parent_setup_on_ctl(self,
                                         parents_modules: list[BaseModule],
                                         switch_parent_ctl : Controller = None,
                                         parents_controllers: list[Controller] = [],
                                         parent_at_start: Controller | BaseModule = None,
                                         ctl_ik_override_names = ["normal"],
                                         ctl_pole_override_names = ["normal", "hand"]
                                         ):
        """
        Override with pre-defined switch controllers : the Ik_limb controller and the Ik_limb pole vector controller
        The first of parents_controllers is the actual outliner parent of the Ik_limb controller

        Since this function happens after mirroring, I use BaseModule.get_actual_component() to get the right side_suffix
        """

        # switch parent on Ik controller
        if not ctl_ik_override_names:
            ctl_ik_override_names = self.CTL_IK_PARENTS_NAME
        ctl_root : Controller = self.get_actual_component(self.ik_fk_limb.ctl_root)
        ctl_ik : Controller = self.get_actual_component(self.ik_fk_limb.ik_limb.ctls[0])
        ctl_ik_parents_controller : list[Controller] = [ctl_root]

        super().build_switch_parent_setup_on_ctl(
            parents_modules=parents_modules,
            parents_controllers=ctl_ik_parents_controller,
            switch_parent_ctl=ctl_ik,
            override_names=ctl_ik_override_names,
            parent_at_start=parent_at_start
        )

        # switch parent on pole vector controller
        if not ctl_pole_override_names:
            ctl_pole_override_names = self.CTL_POLE_PARENTS_NAME

        ctl_pole : Controller = self.get_actual_component(self.ik_fk_limb.ik_limb.ctl_pole)
        ctl_pole_parents_controller : list[Controller] = [
                                                        ctl_root,
                                                        ctl_ik,
                                                        ]
        super().build_switch_parent_setup_on_ctl(
            parents_modules=parents_modules,
            parents_controllers=ctl_pole_parents_controller,
            switch_parent_ctl=ctl_pole,
            override_names=ctl_pole_override_names,
            parent_at_start=ctl_ik
        )

    def build_hinge_setup(self, orient_target_module : BaseModule):
        """
        Create a hinge setup (orient constraint) to make the limb keep its orientation
        """
        # ctl_root = self.get_actual_component(self.ik_fk_limb.ctl_root)
        # normal_parent = cmds.listRelatives(ctl_root.zro_grp_name, parent=1)[0]
        ctl_param : Controller = self.get_actual_component(self.ik_fk_limb.ctl_param)
        ctl_root : Controller = self.get_actual_component(self.ik_fk_limb.ctl_root)
        self.ik_fk_limb.build_hinge(orient_source = orient_target_module.output,
                                    ctl_root = ctl_root,
                                    ctl_param = ctl_param)

    def set_input_and_output(self, input : str = None, output : str = None, input_pos = None, output_pos=None):
        # cmds.xform(self.input, ws=1, t=self.ik_fk_limb.fk_limb.ctls[0].pos)
        # cmds.xform(self.output, ws=1, t=self.ik_fk_limb.fk_limb.ctls[-1].pos)

        super().set_input_and_output(input=self.ik_fk_limb.fk_limb.ctls[0],
                                     output=self.ik_fk_limb.jnts[-1],
                                     input_pos=None,
                                     output_pos=self.ik_fk_limb.fk_limb.ctls[-1].pos
                                     )


        # constraint to controllers
        # cst = cmds.parentConstraint(self.ik_limb.ctl, self.fk_limb.ctls[-1], self.output, mo=False)[0]
        # cmds.connectAttr(f"{self.switch_ctl}.switch_IK_FK", f"{cst}.target[0].targetWeight", f=1)
        # cmds.connectAttr(f"{self.reverse}.outputX", f"{cst}.target[1].targetWeight", f=1)

        #constraint to blend joint chain
        # cmds.parentConstraint(self.ik_fk_limb.jnts[-1], self.output, mo=False)

    def arrange_nodes(self, obj_to_parent=[]):
        obj_to_parent += [
            self.ik_fk_limb.ctl_grp_name,

            self.ik_fk_limb.fk_limb.jnt_grp,

            self.ik_fk_limb.ik_limb.jnt_grp,
        ]

        # conditions if roots haven't been added in the limbs
        if not self.BUILD_ROOT_CTL:
            obj_to_parent += [
                self.ik_fk_limb.fk_limb.ctl_grp_name,
                self.ik_fk_limb.ik_limb.ctl_grp_name,
            ]
        # if the joint chain has been duplicated
        if self.ik_fk_limb.jnt_grp:
            obj_to_parent.append(self.ik_fk_limb.jnt_grp)

        super().arrange_nodes(obj_to_parent)

    def bind_jnts(self, bind_jnts : list[str] = []) -> list[str]:
        bind_jnts += self.ik_fk_limb.bind_jnts()
        return super().bind_jnts(bind_jnts=bind_jnts)

