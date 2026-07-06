from maya import cmds

from devMaya.utils.api import (
    get_hierarchy_list_from_root_node,
    Attribute, Separator, lock_attributes,
    create_jnt_chain_blending,
    create_jnt_chain_translate_blending,
    create_jnt_chain_rotate_blending
)

from devMaya.auto_rig.component.controller import Controller, ControllerShapes
from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from ..component.composed import ComposedComponent
from devMaya.auto_rig.modules.ik_fk import IkFk
from devMaya.auto_rig.component.limb import FkLimb, Limb
from devUi.utils.colors import Colors
from devMaya.auto_rig.decorators import use, UseType

class Foot(BaseModule):

    """
    Feet module for characters

    It is a blending of an ik and fk limb such as an IkFk module

    Feet requires :
    - a joints chain with the ball joint and toe joint

    A Foot can have an instance of IkFk as self._leg,
    It modifies the way it is parented if the parent is the self._leg
    To make the reverse foot roll work

    Adding a reverse roll setup requires 4 joints :
    - back joint
    - inner joint
    - outer joint
    It uses the last joint of the joint chain as front joint

    """

    TYPE = ModuleType.FEET

    CTL_FK_FEET_SHAPE : ControllerShapes | str = "circle"
    CTL_FK_FEET_COLOR : Colors | str  = "green"

    IK_SUFFIX = "_IK"
    CTL_IK_FEET_SHAPE : ControllerShapes | str = "sphere"
    CTL_IK_FEET_COLOR : Colors | str = "red"
    CTL_IK_FEET_SCALE_MULTIPLIER : float = 0.3

    IK_FK_SUFFIX = "_foot"

    WIGGLE_SUFFIX : str = "_wiggle"
    ROLL_SUFFIX : str = "_roll"
    ANKLE_SUFFIX: str = "_ankle"

    CTL_PARAMETER_SUFFIX : str = "_blend"

    def __init__(self, jnt_list:list[str],  leg : IkFk | None, name:str=None, config:Config=None):
        super().__init__(name=name, config=config)
        fk_config = Config({
            "CTL_FK_SHAPE": self.CTL_FK_FEET_SHAPE,
            "CTL_FK_COLOR": self.CTL_FK_FEET_COLOR,
            "SCALE": config.get("SCALE") * 0.7
        })
        config += fk_config

        if isinstance(leg, IkFk):
            self._leg = leg
        else:
            self._leg = None

        self.has_reverse_roll_setup = False

        self._build_feet(jnt_list=jnt_list, config=config)

    def _build_feet(self, jnt_list : list[str], config : Config):
        """
        Create the foot setup with Fk controllers and Ik controllers etc
        """
        # -- -- -- -- Building Blend joint chain
        self.ik_fk_limb = Limb(jnt_list, duplicate_jnt=True, suffix=self.IK_FK_SUFFIX, config=config)


        # -- -- -- -- Building Fk chain
        self.fk_limb = FkLimb(self.ik_fk_limb.jnts, duplicate_jnt=True, config=config)
        cmds.setAttr(f"{self.fk_limb.ctls[-1].shape}.visibility", 0)  # the last ctl of the fk limb is useless
        cmds.setAttr(f"{self.fk_limb.ctls[0].shape}.visibility", 0)  # the first ctl of the fk limb is useless


        # -- -- -- -- Building Ik chain
        # -- -- Building Ik Joints
        self.ik_limb = Limb(self.ik_fk_limb.jnts, suffix=self.IK_SUFFIX, duplicate_jnt=True, config=config)

        # -- -- Building Ik Controllers
        toe_ik_handle = cmds.ikHandle(startJoint=self.ik_limb.jnts[1],
                      endEffector=self.ik_limb.jnts[2],
                      solver='ikRPsolver')[0]
        cmds.parent(toe_ik_handle, self.dont_touch_grp)

        ankle_ik_handle = cmds.ikHandle(startJoint=self.ik_limb.jnts[0],
                      endEffector=self.ik_limb.jnts[1],
                      solver='ikRPsolver')[0]
        cmds.parent(ankle_ik_handle, self.dont_touch_grp)

        # controller for toe
        self.ctl_toe = Controller(self.ik_fk_limb.jnts[1] + self.WIGGLE_SUFFIX)
        self.ctl_toe.pos = self.ik_fk_limb.jnts[1]
        # self.ctl_toe.rot = self.ik_fk_limb.jnts[1]
        self.ctl_toe.shape = self.CTL_FK_FEET_SHAPE
        self.ctl_toe.color = self.CTL_FK_FEET_COLOR
        # self.ctl_toe.shape_rot = [0, 0, 90]
        self.ctl_toe.shape_rot = [90, 0, 90]
        self.ctl_toe.shape_scale = self.SCALE * 0.7
        cmds.parentConstraint(self.ik_fk_limb.jnts[0], self.ctl_toe.zro_grp_name, mo=1)

        # controller for ankle
        self.ctl_reverse_ankle = Controller(self.ik_fk_limb.jnts[1] + self.ANKLE_SUFFIX)
        self.ctl_reverse_ankle.pos = self.ik_fk_limb.jnts[1]
        self.ctl_reverse_ankle.color = self.CTL_IK_FEET_COLOR
        self.ctl_reverse_ankle.shape = self.CTL_IK_FEET_SHAPE
        self.ctl_reverse_ankle.shape_scale = self.SCALE * self.CTL_IK_FEET_SCALE_MULTIPLIER
        cmds.parentConstraint(self.ik_fk_limb.jnts[0], self.ctl_reverse_ankle.zro_grp_name, mo=1)

        self.ik_limb.ctl_grp_name = cmds.group([self.ctl_reverse_ankle.zro_grp_name, self.ctl_toe.zro_grp_name], name=self.CONTROLLER_PREFIX + self.name + self.ROLL_SUFFIX + self.GROUP_SUFFIX)
        self.ik_limb._ctl_chain = [self.ctl_reverse_ankle, self.ctl_toe] # kinda illegal and useless


        # -- -- Building necessary Locators
        # locator for ankle
        self.lct_ankle = cmds.spaceLocator(name=self.LOCATOR_PREFIX + self.ik_fk_limb.jnts[0] + self.ROLL_SUFFIX)[0]
        cmds.xform(self.lct_ankle, ws=True, t=self.fk_limb.ctls[0].pos)
        cmds.pointConstraint(self.lct_ankle, self.ik_limb.jnts[0], mo=1)

        # lct for toe
        self.lct_ball = cmds.spaceLocator(name=self.LOCATOR_PREFIX + self.ik_fk_limb.jnts[1] + self.ROLL_SUFFIX)[0]
        cmds.xform(self.lct_ball, ws=True, t=self.ctl_reverse_ankle.pos)
        # cmds.parentConstraint(self.lct_toe, self.ik_limb.jnts[0], mo=1)
        cmds.parent(self.lct_ankle, self.lct_ball)
        cmds.connectAttr(f"{self.ctl_reverse_ankle}.rotate", f"{self.lct_ball}.rotate")
        # cmds.parentConstraint(self.ctl_reverse_ankle, self.lct_toe, mo=1)
        cmds.parentConstraint(self.lct_ball, ankle_ik_handle, mo=1)

        # locator for toe end
        self.lct_toe_end = cmds.spaceLocator(name=self.LOCATOR_PREFIX + self.ik_fk_limb.jnts[2] + self.ROLL_SUFFIX)[0]
        cmds.xform(self.lct_toe_end, ws=True, t=self.ctl_toe.pos)

        cmds.connectAttr(f"{self.ctl_toe}.rotate", f"{self.lct_toe_end}.rotate")
        cmds.parentConstraint(self.lct_toe_end, toe_ik_handle, mo=1)

        self.lct_wiggle = cmds.spaceLocator(name=self.LOCATOR_PREFIX + self.ik_fk_limb.jnts[0] + self.WIGGLE_SUFFIX)[0]
        cmds.xform(self.lct_wiggle, ws=True, t=self.fk_limb.ctls[1].pos)

        self.lct_grp = cmds.group(name=self.LOCATOR_PREFIX + self.name + self.ROLL_SUFFIX + self.GROUP_SUFFIX, empty=True)
        cmds.parent([self.lct_ball, self.lct_toe_end], self.lct_wiggle)
        cmds.parent(self.lct_wiggle, self.lct_grp)
        cmds.setAttr(f'{self.lct_grp}.visibility', 0)

        # controller param
        self.ik_fk_limb.build_ctl_param(name=self.ik_fk_limb.jnts[0])
        pos = cmds.xform(self.ik_fk_limb.jnts[0], q=1, ws=1, t=1)
        self.ik_fk_limb.ctl_param.pos = [pos[0] + -2 * self.SCALE, pos[1], pos[2]]
        self.ik_fk_limb.ctl_param.shape_rot = [90, 0, 90]
        cmds.parent(self.ik_fk_limb.ctl_param.zro_grp_name, self.ik_limb.ctl_grp_name)

        # attribute
        attr = Attribute(self.CTL_PARAMETER_SUFFIX, type="float", min=0.0, max=1.0, node=self.ik_fk_limb.ctl_param.name)
        attr.add_to_node(node=self.ik_fk_limb.ctl_param.name)

        # connect to visibility of ctl_grp_names
        attr.plug_to(f"{self.ik_limb.ctl_grp_name}.visibility")
        reverse = cmds.createNode("reverse", name=f"rev_{self.ik_fk_limb.jnts[0]}")
        attr.plug_to(f"{reverse}.inputX")
        cmds.connectAttr(f"{reverse}.outputX", f"{self.fk_limb.ctl_grp_name}.visibility")

        # connexions between joints
        create_jnt_chain_rotate_blending(self.ik_limb.jnts, self.fk_limb.jnts, self.ik_fk_limb.jnts, str(attr))
        create_jnt_chain_translate_blending(self.ik_limb.jnts[1:], self.fk_limb.jnts[1:], self.ik_fk_limb.jnts[1:], str(attr))

        # joints visibility
        cmds.setAttr(f'{self.ik_limb.jnt_grp}.visibility', 0)
        cmds.setAttr(f'{self.fk_limb.jnt_grp}.visibility', 0)

    @use(UseType.UNIQUE | UseType.UNNECESSARY)
    def build_reverse_roll_setup(self, outer_jnt:str, inner_jnt:str, back_jnt:str):
        """
        Create the reverse roll setup with several pivot points for each side
        """
        front_jnt = self.ik_fk_limb.jnts[2]

        roll_jnts = [front_jnt, inner_jnt, outer_jnt, back_jnt]
        roll_lcts = []
        roll_ctls = []

        for i, jnt in enumerate(roll_jnts):
            ctl = Controller(jnt)
            ctl.pos = jnt
            ctl.color = self.CTL_IK_FEET_COLOR
            ctl.shape = self.CTL_IK_FEET_SHAPE
            ctl.shape_scale = self.SCALE * self.CTL_IK_FEET_SCALE_MULTIPLIER

            lct = cmds.spaceLocator(name=self.LOCATOR_PREFIX + jnt + self.ROLL_SUFFIX)[0]
            cmds.xform(lct, ws=True, t=ctl.pos)
            cmds.connectAttr(f"{ctl.name}.rotate", f"{lct}.rotate")

            roll_lcts.append(lct)
            roll_ctls.append(ctl)

            if i>0:
                cmds.parent(roll_lcts[i], roll_lcts[i-1])

        cmds.parent([ctl.zro_grp_name for ctl in roll_ctls], self.ik_limb.ctl_grp_name)

        cmds.parent(roll_lcts[0], self.lct_grp)
        cmds.parent(self.lct_wiggle, roll_lcts[-1])

        self.has_reverse_roll_setup = True

    def set_parent_module(self, parent : BaseModule, maintain_offset=True):
        """
        Re implement creating parent and child relationship if it has a self._leg
        That way we avoid cycling
        """
        if not self._leg:
            # If it has not self._leg, then it doesn't need a special behavior at all
            super().set_parent_module(parent=parent, maintain_offset=maintain_offset)
            return

        leg_name = self.get_actual_component(self._leg.name)

        if parent.name != leg_name:
            # If you want to parent the foot module to another module than its self._leg
            super().set_parent_module(parent=parent, maintain_offset=maintain_offset)
            return

        # You are trying to parent the feet to its self._leg
        # so implement a special behavior to parent constraint

        # Ik limb
        ctl_ik_leg = self.get_actual_component(self._leg.ik_fk_limb.ik_limb.ctls[0])
        cmds.parentConstraint(ctl_ik_leg, self.get_actual_component(self.ik_limb.ctl_grp_name), mo=1)
        cmds.parentConstraint(ctl_ik_leg, self.get_actual_component(self.ik_limb.jnt_grp), mo=1)
        cmds.parentConstraint(ctl_ik_leg, self.get_actual_component(self.lct_grp), mo=1)

        # Fk limb
        ctl_fk_leg_end = self.get_actual_component(self._leg.ik_fk_limb.fk_limb.ctls[-1])
        cmds.parentConstraint(ctl_fk_leg_end, self.get_actual_component(self.fk_limb.ctls[0].zro_grp_name), mo=1)
        # cmds.scaleConstraint(ctl_fk_leg_end, self.get_actual_component(self.fk_limb.ctls[0].zro_grp_name), mo=1)
        cmds.parentConstraint(ctl_fk_leg_end, self.get_actual_component(self.fk_limb.jnt_grp), mo=1)

        # Blend limb
        jnt_ik_fk_leg_end = self.get_actual_component(self._leg.ik_fk_limb.jnts[-1])
        cmds.pointConstraint(jnt_ik_fk_leg_end, self.get_actual_component(self.ik_fk_limb.jnts[0]), mo=1) #0
        # cmds.scaleConstraint(jnt_ik_fk_leg_end, self.get_actual_component(self.ik_fk_limb.jnts[0]), mo=1)

        # hide self.ctl_param
        ctl_param = self.get_actual_component(self.ik_fk_limb.ctl_param)
        cmds.setAttr(f"{ctl_param.zro_grp_name}.visibility", 0)

        # leg ctl_param
        ctl_param_leg = self.get_actual_component(self._leg.ik_fk_limb.ctl_param)

        # connect leg ctl_param attribute to foot switch limb attribute
        attr = Attribute(self._leg.ik_fk_limb.IK_FK_SUFFIX, type="float", min=0.0, max=1.0, node=ctl_param_leg.name)
        attr.plug_to(f"{ctl_param}.{self.CTL_PARAMETER_SUFFIX}")

        # constraint the leg ik handle to the lct[-1]
        cmds.parentConstraint(self.get_actual_component(self.lct_ankle), self.get_actual_component(self._leg.ik_handle()), mo=1)

        # blend jnt_grp rotate
        create_jnt_chain_rotate_blending([self.get_actual_component(self.ik_limb.jnt_grp)],
                                         [self.get_actual_component(self.fk_limb.jnt_grp)],
                                         [self.get_actual_component(self.ik_fk_limb.jnt_grp)],
                                         f"{ctl_param}.{self.CTL_PARAMETER_SUFFIX}"
                                         )

        if self.has_reverse_roll_setup:
            pass

        self.parents = [parent]
        parent.children += [self]

    def arrange_nodes(self, obj_to_parent):
        """
        Parent all the elements under module input
        """
        obj_to_parent += [
            self.lct_grp,

            self.ik_fk_limb.jnt_grp,

            self.fk_limb.jnt_grp,
            self.fk_limb.ctl_grp_name,

            self.ik_limb.jnt_grp,
            self.ik_limb.ctl_grp_name,
        ]
        super().arrange_nodes(obj_to_parent)

    def set_input_and_output(self):
        """
        Position lct in to the right place
        Position and constraints lct out to the right place
        """
        super().set_input_and_output(input=self.ik_fk_limb.jnts[0], output=self.ik_fk_limb.jnts[-1])
        # cmds.xform(self.input, ws=1, t=cmds.xform(self.ik_fk_limb.jnts[0], q=1, ws=1, t=1))
        # cmds.xform(self.output, ws=1, t=cmds.xform(self.ik_fk_limb.jnts[-1], q=1, ws=1, t=1))

    def bind_jnts(self, bind_jnts:list[str]) -> list[str]:
        bind_jnts += self.ik_fk_limb.bind_jnts()
        return super().bind_jnts(bind_jnts=bind_jnts)

    @property
    def leg(self):
        return self._leg

    @leg.setter
    def leg(self, leg: IkFk):
        if not isinstance(leg, IkFk):
            print("Cannot set leg because", leg, "is not an instance of Leg :", type(leg))
            return
        self._leg = leg
