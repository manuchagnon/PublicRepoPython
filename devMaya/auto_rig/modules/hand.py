from maya import cmds

from devMaya.utils.api import (
    get_hierarchy_list_from_root_node,
    Attribute, Separator, lock_attributes,
)

from devMaya.auto_rig.component.controller import Controller
from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.component.limb import FkLimb
from devMaya.auto_rig.modules.simple import Simple
from devMaya.auto_rig.decorators import use, UseType

class Finger(FkLimb):

    CTL_METACARPUS_SHAPE = "box on floor"
    CTL_METACARPUS_COLOR = "pink"

    def __init__(self, jnt_list:list[str], config:Config=None):

        super().__init__(jnt_list=jnt_list[1:], config=config)
        # print(self.jnts)
        self.ctl_metacarpus = Controller(jnt_list[0])
        self.ctl_metacarpus.shape = self.CTL_METACARPUS_SHAPE
        self.ctl_metacarpus.color = self.CTL_METACARPUS_COLOR

        jnt = cmds.joint(name=self.JOINT_PREFIX + self.ctl_metacarpus._name)
        cmds.select(clear=True)

        cmds.matchTransform(self.ctl_metacarpus.zro_grp_name, jnt_list[0], pos=1, rot=1)
        cmds.parent(self.ctls[0].zro_grp_name, self.ctl_metacarpus)
        cmds.parent(self.ctl_metacarpus.zro_grp_name, self.ctl_grp_name)

        cmds.parent(self.jnt_grp, self.ctl_metacarpus)
        cmds.parent(jnt, self.jnt_grp)
        cmds.parent(self.jnts[0], jnt)
        self._jnt_chain.insert(0, jnt)

        self.ctl_rot = None
        self.rot_grps : list[str] = []

        self._rescale_ctls()

    def _rescale_ctls(self):
        # Rescale Metacarpus
        length = cmds.getAttr(f"{self.ctls[0].zro_grp_name}.translateX")
        # self.ctl_metacarpus.shape_scale = [self.SCALE * length, self.SCALE * 1.4, self.SCALE/2]
        # cmds.move(length/2, 0, 0, self.ctl_metacarpus.cvs, r=1, wd=1, os=1)

        self.ctl_metacarpus.shape_rot = [0, 0, -90]
        self.ctl_metacarpus.shape_scale = [self.SCALE * length, self.SCALE * 1.4, self.SCALE/2]
        # self.ctl_metacarpus.shape_scale = self.SCALE * self.SCALE_MULTIPLIER

        # Rescale Phalanxes
        for i, ctl in enumerate(self.ctls):
            ctl.shape_scale = 0.80 ** i

    def build_rotation_setup(self) -> Controller:
        """
        Create a ctl and the quick rotation, setup
        """
        ctl = Controller(self.jnts[0] + "_quick_rotation")
        ctl.shape = "sphere"
        ctl.color = "yellow"
        ctl.shape_scale = 0.25* self.SCALE
        cmds.matchTransform(ctl.zro_grp_name, self.ctl_metacarpus, pos=1, rot=1)
        rot_grps = super().build_quick_rotation_setup(ctl_target_rotation=ctl)

        cmds.parent(ctl.zro_grp_name, self.ctl_metacarpus)
        cmds.xform(ctl, os=1, t = [0, self.SCALE*2, 0])

        self.ctl_rot = ctl
        self.rot_grps = rot_grps

        return ctl

    def __repr__(self):
        return self.name

class Hand(Simple):

    """
    Hand module for characters

    Works with more or less than five fingers

    Hand requires :
    - a joint for the start of the hand

    Adding Finger requires:
    - a joint chain which first joint is the metacarpus bones inside the hand,
    followed by as many phalanxes as needed

    You must add fingers in the right order, otherwise the rotations setup will fail
    """

    TYPE = ModuleType.HAND

    CTL_HAND_SHAPE = "box"
    CTL_HAND_COLOR = "green"

    CORRECTIVE_TRANSLATE_MULTIPLIER = 0.2

    CTL_QUICK_ROT_SUFFIX = "_quick_rot"

    def __init__(self, jnt:str, name:str=None, config:Config=None):
        new_config = Config({
            "CTL_COLOR" : self.CTL_HAND_COLOR,
            "CTL_SHAPE" : self.CTL_HAND_SHAPE,
        })
        hand_config = new_config + config
        super().__init__(jnt=jnt, name=name, config=hand_config)

        self.lct_orient = cmds.spaceLocator(name=self.LOCATOR_PREFIX + self.name)
        cmds.xform(self.lct_orient, ws=1, t=self.ctls[0].pos, ro=self.ctls[0].rot)
        cmds.orientConstraint(self.lct_orient, self.ctls[0].zro_grp_name, mo=True)

        self._fingers:list[Finger] = []

    @use(UseType.MULTIPLE | UseType.EXCLUDING)
    def add_finger(self, jnt:str):
        """
        Add a finger to the hand module by providing the first jnt of its jnt_chain
        """
        jtn_chain = get_hierarchy_list_from_root_node(root=jnt, reverse=False)
        finger_jnt_chain = jtn_chain[:-1]
        finger_config = Config({
            "CORRECTIVE_TRANSLATE_MULTIPLIER": self.SCALE * self.CORRECTIVE_TRANSLATE_MULTIPLIER,
            })
        finger = Finger(jnt_list=finger_jnt_chain, config=finger_config)
        self._fingers.append(finger)
        cmds.parent(finger.ctl_grp_name, self.ctl)

    @use(UseType.UNIQUE | UseType.EXCLUDING)
    def add_fingers(self, jnts:list[str]):
        """
        Add multiple fingers to the hand module by providing the first jnt of each jnt_chain
        """
        for jnt in jnts:
            self.add_finger(jnt)

    @use(UseType.UNIQUE | UseType.UNNECESSARY)
    def build_rotation_setup(self):
        """
        Create a ctl that is connected to finger's Fk controllers rotate, to get quick finger poses
        """
        if not self._fingers:
            print("Build Finger first")
            return
        for finger in self._fingers:
            finger.build_rotation_setup()

    @use(UseType.UNIQUE | UseType.UNNECESSARY)
    def build_spread_setup(self, excluded_fingers_indexes :list[int] | int=[]):
        """
        Create a ctl_rot that is connected to finger's first controller, to quickly spread fingers
        Also create a ctl_rot that is connected to finger's metacarpus controller, to quickly metacarpus controllers
        """
        if not self._fingers:
            print("Build Finger first")
            return
        # You probably want to exclude a finger from the setup (thumb)
        if excluded_fingers_indexes:
            if isinstance(excluded_fingers_indexes, int):
                excluded_fingers_indexes = [excluded_fingers_indexes]
            focused_fingers = [self._fingers[i]
                               for i in range(len(self._fingers))
                               if i not in excluded_fingers_indexes]
        else:
            focused_fingers = self._fingers

        finger_amount = len(focused_fingers)

        # Create two controllers rot
        def create_ctl_rot(suffix:str, shape:str, color:str, distance_mult:float) -> Controller:
            ctl_rot = Controller(name=self.name + self.CTL_QUICK_ROT_SUFFIX + suffix)
            ctl_rot.shape = shape
            ctl_rot.color = color
            ctl_rot.shape_rot = [0, -90, 0]
            ctl_rot.line_width = 2
            ctl_rot.shape_scale = self.SCALE*0.5
            cmds.matchTransform(ctl_rot.zro_grp_name, self.ctl, position=True, rotation=True)
            cmds.parent(ctl_rot.zro_grp_name, self.ctl)
            cmds.xform(ctl_rot.zro_grp_name, os=1, t=[distance_mult * self.SCALE, 0, 0])
            return ctl_rot

        ctl_main_rot = create_ctl_rot(suffix="_fingers", shape="triangle", color="yellow", distance_mult=4.0)
        lock_attributes(ctl_main_rot.name, attr_name=["tx", "ty", "tz"])

        ctl_meta_rot = create_ctl_rot(suffix="_metacarpus", shape="square", color="pink", distance_mult=3.3)
        ctl_meta_rot.shape_scale = [0.3, 1, 1]
        lock_attributes(ctl_meta_rot.name, attr_name=["ry", "rz", "tx", "ty", "tz"])

        for i, finger in enumerate(focused_fingers):
            # Main Rotations for fingers first controller
            if finger.ctl_rot:
                pma = cmds.createNode("plusMinusAverage", name="pma_" + finger.name)
                rotate = Attribute(long_name="rotate")
                rotate.build_attribute_from_node(node=finger.ctl_rot)
                for connexion in rotate.output_connexions:
                    cmds.connectAttr(f"{pma}.output3D", connexion, f=1)
                cmds.connectAttr(f"{finger.ctl_rot}.rotate", f"{pma}.input3D[0]")
                cmds.connectAttr(f"{ctl_main_rot}.rotateZ", f"{pma}.input3D[1].input3Dz")
            else:
                finger.build_quick_rotation_setup(ctl_target_rotation=ctl_main_rot)

            # Create setup for first finger controller and metacarpus controller
            # Spread with scale Z
            # Rotates with rotate X
            def create_spread_setup(ctl_rot:Controller, ctl_target:Controller):
                def remap_channel(index: int, attr_source: str, attr_target: str, flat_multiplier=1.0):
                    index_at_zero = (finger_amount-1)/2
                    rot_multiplier = 1/finger_amount

                    result = (index-index_at_zero) * flat_multiplier * rot_multiplier

                    mult = cmds.createNode("multDoubleLinear", name="mult_" + attr_source + ctl_rot.name)
                    cmds.setAttr(f"{mult}.input2", result)
                    cmds.connectAttr(f"{mult}.output", f"{rot_grp}.{attr_target}")

                    return mult

                rot_grp = ctl_target.add_offset_grp(suffix="_ROTbis")
                mult_rx = remap_channel(i, attr_source="rotateX", attr_target="rotateZ", flat_multiplier=1.5)
                cmds.connectAttr(f"{ctl_rot.name}.rotateX", f"{mult_rx}.input1")

                mult_sx = remap_channel(i, attr_source="scaleZ", attr_target="rotateY", flat_multiplier=50.0)
                minus = cmds.createNode("addDoubleLinear", name="adl_minus_one_" + ctl_rot.name)
                cmds.connectAttr(f"{ctl_rot.name}.scaleZ", f"{minus}.input1")
                cmds.setAttr(f"{minus}.input2", -1)
                cmds.connectAttr(f"{minus}.output", f"{mult_sx}.input1", f=1)

            create_spread_setup(ctl_rot=ctl_main_rot, ctl_target=finger.ctls[0])
            create_spread_setup(ctl_rot=ctl_meta_rot, ctl_target=finger.ctl_metacarpus)

    @use(UseType.UNIQUE | UseType.UNNECESSARY)
    def build_corrective_jnts(self, rot_axis="Z", trans_axis="Y"):
        """
        Create a corrective joint setup for all fingers,
        with tweakable attributes on each Controller to fine tune joint translateX
        """
        for finger in self._fingers:
            finger.build_corrective_jnts_setup(rot_axis=rot_axis, trans_axis=trans_axis)

    def bind_jnts(self, bind_jnts:list[str]) -> list[str]:
        jnts = [jnt for jnt in [finger.jnts for finger in self._fingers]]
        bind_jnts += jnts
        return super().bind_jnts(bind_jnts=bind_jnts)

    def set_input_and_output(self, input : str =None, output : str = None, input_pos=None, output_pos=None):
        super().set_input_and_output(input=self.ctls[0], output=self.ctls[0])
        # cmds.xform(self.input, ws=1, t=self.ctls[0].pos)
        # cmds.xform(self.output, ws=1, t=self.ctls[0].pos)

    def arrange_nodes(self, obj_to_parent=[]):
        obj_to_parent += [
            self.lct_orient,
        ]
        super().arrange_nodes(obj_to_parent=obj_to_parent)