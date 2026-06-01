from pprint import pprint

from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.component.ribbon import LimbRibbon
from devMaya.utils.api import (rotate_ctl,
                               lock_attributes,
                               get_pole_vector_placement,
                               create_annotation,
                               add_separator_attribute
                               )
from ..component.controller import Controller
from ..component.base import BaseComponent, ComponentType
from ..configs.config import Config
from ...utils.attribute import connect_attributes
from ...utils.name import determine_component_name


class Limb(BaseComponent):
    """
    A Limb module contains :
        - a joint chain, must be well oriented at the beginning
        - a joint group
    Methods :
        - add offset controller and joint
    """

    TYPE = ComponentType.LIMB
    CTL_BENDY_COLOR = "red"
    CTL_BENDY_SHAPE = "round square"
    CTL_BENDY_SUFFIX = "_offset"

    CTL_ROOT_COLOR = "pink"
    CTL_ROOT_SHAPE = "box"
    CTL_ROOT_SUFFIX = "_root"

    CTL_OFFSET_DENSITY = 3

    def __init__(self, jnt_list:  list[str], name=None, duplicate_jnt=False, suffix="", config: Config = None):
        super().__init__(name, config=config)

        self._ctl_chain = []
        self.jnt_grp = None
        self._jnt_chain = jnt_list

        self._has_offset_jnt = False
        self._offset_jnt_chain = []
        self.offset_ctl_chain = []

        self.ctl_root = None
        self.ctl_grp_name = None

        self._is_bendy = False

        if not duplicate_jnt:
            self._jnt_chain = jnt_list
        else:
            self._jnt_chain = self._duplicate_jnt_chain(jnt_list, suffix=suffix)

    def _duplicate_jnt_chain(self, jnt_list: list[str], suffix: str ="") -> list[str]:
        """
        Create a duplicate of the joint chain with new suffix
        """
        self.jnt_grp = cmds.group(empty=True, name=jnt_list[0] + suffix + self.GROUP_SUFFIX)

        jnt_created = []

        for jnt in jnt_list:
            new_jnt_name = determine_component_name(jnt, prefix=self.JOINT_PREFIX, suffix=suffix, side_suffixes=self.SIDE_SUFFIXES)

            # has_side_one, has_side_two  = self.SIDE_SUFFIXES[0] in jnt, self.SIDE_SUFFIXES[1] in jnt
            # if self.JOINT_PREFIX in jnt:
            #     if has_side_one:
            #         new_jnt_name = jnt.split(self.SIDE_SUFFIXES[0])[0] + suffix + self.SIDE_SUFFIXES[0]
            #     elif has_side_two:
            #         new_jnt_name = jnt.split(self.SIDE_SUFFIXES[1])[0] + suffix + self.SIDE_SUFFIXES[1]
            #     else:
            #         jnt + suffix + self.side_suffix
            # elif has_side_one:
            #     new_jnt_name = self.JOINT_PREFIX + jnt.split(self.SIDE_SUFFIXES[0])[0] + suffix + self.SIDE_SUFFIXES[0]
            # elif has_side_two:
            #     new_jnt_name = self.JOINT_PREFIX + jnt.split(self.SIDE_SUFFIXES[1])[0] + suffix + self.SIDE_SUFFIXES[1]
            # else:
            #     new_jnt_name = self.JOINT_PREFIX + jnt + suffix + self.side_suffix

            cmds.select(clear=1)
            new_jnt = cmds.joint(n=new_jnt_name)

            cmds.matchTransform(new_jnt, jnt)
            cmds.makeIdentity(new_jnt, apply=1, t=1, r=1, s=1)

            # for axis in ["X", "Y", "Z"]:
            #     cmds.setAttr(f'{new_jnt}.jointOrient{axis}', 0)

            jnt_created.append(new_jnt)

        cmds.parent(jnt_created[0], self.jnt_grp)

        for i in range(1, len(jnt_created)):
            cmds.parent(jnt_created[i], jnt_created[i-1])

        return jnt_created

    def add_offset_grp_on_ctl(self, gizmo_status = 0, gizmo_target_obj: str | None = None, suffix: str | None = None) -> list[str] :
        """
        Create offset groups on every controller of the limb, useful for adding other layer of mechanism
        """
        new_offset_grps = [ctl.add_offset_grp(gizmo_status, gizmo_target_obj, suffix) for ctl in self.ctls]

        return new_offset_grps

    def build_root_ctl(self) -> Controller:
        """
        Create a root controller which is the parent of the whole limb
        """
        start_joint = self.jnts[0]
        ctl = Controller(name=start_joint + self.CTL_ROOT_SUFFIX)
        ctl.shape = self.CTL_ROOT_SHAPE
        ctl.color = self.CTL_ROOT_COLOR
        ctl.shape_scale = self.SCALE * 0.7
        ctl.pos = cmds.xform(start_joint, q=1, ws=1, t=1)
        ctl.rot = cmds.xform(start_joint, q=1, ws=1, ro=1)

        if self.ctls:
            cmds.parent(ctl.zro_grp_name, self.ctl_grp_name)
            cmds.parent(self.ctls[0].zro_grp_name, ctl)
        else:
            cmds.parent(self.jnts[0], ctl.zro_grp_name)
        self.ctl_root = ctl
        print("called root", self.ctl_root)
        # self._ctl_chain.insert(0, ctl)

        return ctl

    def build_offset_ctl(self):
        """
        Create a new controller with a joint inside under every controller of the limb,
        In order to have full control of the limb
        Doesn't work if the limb is bendy
        """
        if self._is_bendy:
            return

        self._offset_jnt_chain = []

        for jnt in self.jnts:
            ctl = Controller(jnt + self.CTL_BENDY_SUFFIX)
            ctl.color = self.CTL_BENDY_COLOR
            ctl.shape = self.CTL_BENDY_SHAPE
            ctl.shape_scale = self.SCALE * 0.7
            ctl.shape_rot = (0, 0, 90)

            offset_jnt = cmds.joint(name=jnt + self.CTL_BENDY_SUFFIX)
            self._offset_jnt_chain.append(offset_jnt)
            cmds.select(clear=1)

            # cmds.parent(offset_jnt, ctl)
            cmds.matchTransform(ctl.zro_grp_name, jnt)
            cmds.parent(ctl.zro_grp_name, jnt)

            self.offset_ctl_chain.append(ctl)

        self._has_offset_jnt = True

    def build_bendy(self,
            flc_on_u=None,
            flc_on_v=1,

            flc_param_u_start=0,
            flc_param_u_end=1,
            flc_param_u_offset=0,

            flc_param_v_start=0,
            flc_param_v_end=1,
            flc_param_v_offset=0
            ):
        """
        Create bendy mechanism on this limb with a ribbon component
        """

        # build offset controllers if they aren't already set
        if not self._has_offset_jnt:
            self.build_offset_ctl()

        # build ribbon
        if not flc_on_u:
            flc_on_u = (self.CTL_OFFSET_DENSITY * (len(self.jnts)-1)) + len(self.jnts)
        self._is_bendy = True

        ribbon = LimbRibbon(self._jnt_chain, name=self.name, config=self._config)

        ribbon.distribute_follicles(
            flc_on_u=flc_on_u,
            flc_on_v=flc_on_v,

            flc_param_u_start=flc_param_u_start,
            flc_param_u_end=flc_param_u_end,
            flc_param_u_offset=flc_param_u_offset,

            flc_param_v_start=flc_param_v_start,
            flc_param_v_end=flc_param_v_end,
            flc_param_v_offset=flc_param_v_offset,
        )
        ribbon.add_offset_ctls()
        ribbon.add_jnts()

        self.ribbon = ribbon

        # Build new offset controllers and joints to skin the ribbon
        index = 0
        for ctl_start, ctl_end, jnt in zip(self.offset_ctl_chain[:], self.offset_ctl_chain[1::], self._jnt_chain[:]):
            ctl_offset = Controller(ctl_start.name + "_bis")
            ctl_offset.color = self.CTL_BENDY_COLOR
            ctl_offset.shape = self.CTL_BENDY_SHAPE
            ctl_offset.shape_rot = [0, 0, 90]
            ctl_offset.shape_scale = self.SCALE * 0.7

            offset_jnt = cmds.joint(name=jnt + self.CTL_BENDY_SUFFIX + "_bis")
            cmds.select(clear=1)

            # Point matrix
            mult_matrix_start = cmds.createNode("multMatrix", n=f'{ctl_offset}_mm_start')
            # mult_matrix_end = cmds.createNode("multMatrix", n=f'{ctl_offset}_mm_end')
            decompose_matrix = cmds.createNode("decomposeMatrix", n=f'{ctl_offset}_dm')
            blend_matrix = cmds.createNode("blendMatrix", n=f'{ctl_offset}_bm')

            # Connect point matrix constraint
            cmds.connectAttr(f'{ctl_start}.worldMatrix[0]', f'{blend_matrix}.inputMatrix', f=1)
            cmds.connectAttr(f'{ctl_end}.worldMatrix[0]', f'{blend_matrix}.target[0].targetMatrix', f=1)
            cmds.setAttr(f'{blend_matrix}.envelope', 0.5)

            cmds.connectAttr(f'{blend_matrix}.outputMatrix', f'{mult_matrix_start}.matrixIn[0]', f=1)
            cmds.connectAttr(f'{ctl_offset.zro_grp_name}.parentInverseMatrix[0]', f'{mult_matrix_start}.matrixIn[1]', f=1)

            cmds.connectAttr(f'{mult_matrix_start}.matrixSum', f'{decompose_matrix}.inputMatrix')
            cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{ctl_offset.zro_grp_name}.translate')

            # Aim constraint
            cmds.aimConstraint(ctl_end, ctl_offset.zro_grp_name, mo=0, weight=1, aimVector=[1, 0, 0],
                               upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=ctl_end.zro_grp_name)

            cmds.parent(ctl_offset.zro_grp_name, jnt)

            # Inserting newly created offset controller and joint inside their lists for further uses next
            index = self.offset_ctl_chain.index(ctl_start) + 1
            self._offset_jnt_chain.insert(index, offset_jnt)
            self.offset_ctl_chain.insert(index, ctl_offset)

        # Skin the ribbon
        cmds.skinCluster(
            self._offset_jnt_chain,
            ribbon.name,
            n=f'{ribbon.name}_skinCluster',
            maximumInfluences=4,
            dropoffRate=3.0,
            obeyMaxInfluences=1
        )

    @property
    def jnts(self):
        if self._has_offset_jnt:
            if self._is_bendy:
                return self.ribbon.jnts
            else:
                return self._offset_jnt_chain
        else:
            return self._jnt_chain

    @property
    def jnt(self):
        return self._jnt_chain[-1]

    @property
    def ctls(self):
        return self._ctl_chain

    @property
    def ctl(self):
        return self._ctl_chain[-1]


class FkLimb(Limb):
    """
    A FkLimb module contains :
        - a joint chain
        - a ctl group
        - a FK ctl chain
    """

    TYPE = ComponentType.FK_LIMB
    FK_SUFFIX = "_FK"
    CTL_FK_COLOR = "green"
    CTL_FK_SHAPE = "circle"

    def __init__(self, jnt_list:  list[str], duplicate_jnt=True, config: Config=None):

        if jnt_list == []:
            self._ctl_chain = []
            self.ctl_grp_name = None
            cmds.error("Empty FK limb")
            return

        # duplicate the joint chain with '_FK' suffix and store it
        super().__init__(jnt_list, duplicate_jnt=duplicate_jnt, suffix=self.FK_SUFFIX, config=config)

        ctl_chain = [
            Controller.CONTROLLER_PREFIX + jnt.split(self.JOINT_PREFIX, 1)[-1]
            for jnt in self.jnts
        ]

        # if ctl already exist
        if all([cmds.objExists(ctl) for ctl in ctl_chain]):
            self.build_from_scene_data(self.jnts)
        else:
            self.build(self.jnts)

    def build(self, jnt_list: list[str]):
        """
        Build the FK limb by creating Fk ctl on the jnt chain and store them in self._ctl_chain
        """
        self._ctl_chain = []
        for jnt in jnt_list:
            ctl = Controller(jnt)
            ctl.shape = self.CTL_FK_SHAPE
            ctl.shape_scale = self.SCALE
            ctl.color = self.CTL_FK_COLOR
            ctl.pos = cmds.xform(jnt, q=1, ws=1, t=1)
            ctl.rot = cmds.xform(jnt, q=1, ws=1, ro=1)
            rotate_ctl(ctl, "Z", 90)
            self._ctl_chain.append(ctl)

        self.ctl_grp_name = cmds.group(self._ctl_chain[0].zro_grp_name, name=self._ctl_chain[0].name + self.GROUP_SUFFIX)

        for i in range(1, len(self._ctl_chain)):
            cmds.parent(self._ctl_chain[i].zro_grp_name, self._ctl_chain[i - 1].name)

        for ctl, jnt in zip(self.ctls, self.jnts):
            cmds.pointConstraint(ctl.name, jnt, w=1)
            cmds.orientConstraint(ctl.name, jnt, w=1)
            # cmds.connectAttr(f"{ctl}.rotate", f"{jnt}.rotate")
            # cmds.connectAttr(f"{ctl}.translate", f"{jnt}.translate")

    def build_from_scene_data(self, jnt_list: list[str]):
        """
        Build the FK limb by storing already existing ctl in self._ctl_chain
        Parent them if they aren't already
        (Maybe it's not necessary to rebuild from scene data, i will see)
        """

        self._ctl_chain = []
        for jnt in jnt_list:
            ctl = Controller(jnt)
            self._ctl_chain.append(ctl)

        for i in range(len(self._ctl_chain)):
            if i > 0:
                try:
                    cmds.parent(self._ctl_chain[i].name, self._ctl_chain[i - 1].zro_grp_name)
                except:
                    continue


class IkLimb(Limb):
    """
    A FkLimb module contains :
        - a joint chain
        - a ctl group
        - an IK ctl
    Methods :
        - add pole vector
        - bendy
        (- stretchy)
    """

    TYPE = ComponentType.IK_LIMB

    IK_SUFFIX = "_IK"
    POLE_VECTOR_SUFFIX = "_pole_vector"
    POLE_VECTOR_DISTANCE = 8
    IK_HANDLE_SUFFIX = "_ik_handle"

    CTL_IK_COLOR = "red"
    CTL_IK_SHAPE = "box"
    CTL_IK_SCALE = 1.3

    CTL_POLE_SHAPE = "sphere"

    STRETCH_SUFFIX = "_stretch"

    def __init__(self, jnt_list: list[str], pole_vector=False, stretchy=False, duplicate_jnt=True, config: Config=None):

        if jnt_list == []:
            self._ctl_chain = []
            self.ctl_grp_name = None
            self.ik_handle = None
            cmds.error("Empty IK limb")
            return

        # duplicate the joint chain with '_IK' suffix and store it
        super().__init__(jnt_list, duplicate_jnt=duplicate_jnt, suffix=self.IK_SUFFIX, config=config)
        self.stretch_jnt_chain = []

        if cmds.objExists(Controller.CONTROLLER_PREFIX + jnt_list[-1] + self.IK_SUFFIX):
            self.build_from_scene_data(self.jnts)
        else:
            self.build(self.jnts)

        if pole_vector:
            self.build_pole_vector()
        if stretchy:
            self.build_stretchy()

    # -- Builders

    def build(self, jnt_list: list[str]):
        """
        Build the IK limb by creating Ik ctl on the last jnt and store it in self._ctl_chain
        """

        ctl = Controller(self.jnts[-1])
        ctl.shape = self.CTL_IK_SHAPE
        ctl.shape_scale = self.SCALE * self.CTL_IK_SCALE
        ctl.color = self.CTL_IK_COLOR
        ctl.pos = cmds.xform(self.jnts[-1], q=1, ws=1, t=1)
        ctl.rot = cmds.xform(self.jnts[-1], q=1, ws=1, ro=1)

        cmds.connectAttr(f"{ctl}.rotate", f"{self.jnts[-1]}.rotate")


        self.ik_handle = cmds.ikHandle(name=ctl.name + self.IK_HANDLE_SUFFIX,
                                  startJoint=self.jnts[0],
                                  endEffector=self.jnts[-1],
                                  solver='ikRPsolver')[0]

        cmds.parent(self.ik_handle, ctl)

        self.ctl_grp_name = cmds.group(ctl.zro_grp_name, name=ctl.name + self.GROUP_SUFFIX)

        self._ctl_chain = [ctl]

    def build_from_scene_data(self, jnt_list: list[str]):
        pass

    def build_pole_vector(self):
        if not len(self._jnt_chain) == 3:
            return

        lct = get_pole_vector_placement(*self.jnts, scale=self.SCALE * self.POLE_VECTOR_DISTANCE)
        new_lct_name = f"{self.LOCATOR_PREFIX}{self.ctl}{self.POLE_VECTOR_SUFFIX}"
        cmds.rename(lct, new_lct_name)
        lct = new_lct_name

        cmds.poleVectorConstraint(lct, self.ik_handle, w=1)
        cmds.setAttr(f'{lct}Shape.visibility', 0)

        create_annotation(self.jnts[1], lct)

        ctl = Controller(self.ctls[0].name + self.POLE_VECTOR_SUFFIX)
        ctl.shape = self.CTL_POLE_SHAPE
        ctl.shape_scale = self.SCALE * 0.2
        ctl.color = self.CTL_IK_COLOR
        ctl.pos = cmds.xform(lct, q=1, ws=1, t=1)
        ctl.rot = cmds.xform(lct, q=1, ws=1, ro=1)

        cmds.parent(ctl.zro_grp_name, self.ctl_grp_name)
        cmds.parent(lct, ctl)

        self.ctl_pole = ctl

    def build_root_ctl(self) -> Controller:
        """
        Override the method to make it able to move the joint chain
        """
        ctl = super().build_root_ctl()
        cmds.parentConstraint(ctl, self.jnts[0], mo=True)
        if self.stretch_jnt_chain:
            cmds.pointConstraint(self.ctl_root, self.stretch_jnt_chain[0], mo=False)
        return ctl

    def build_stretchy(self):
        """
        Create a stretch mechanism on this Ik Limb with a distance and translate X conversion
        TO DO:
        implement global scale conversion, because scale would not work with this setup alone
        """
        grp = self.jnt_grp
        self.stretch_jnt_chain = self._duplicate_jnt_chain(self._jnt_chain, suffix=self.STRETCH_SUFFIX)
        cmds.parent(self.jnt_grp, grp)
        self.jnt_grp = grp

        max_dist = sum([cmds.getAttr(f"{jnt}.translateX") for jnt in self.stretch_jnt_chain[1:]])

        dist = cmds.createNode("distanceBetween", n=f"{self.ctl}_db")
        # distance_value = cmds.getAttr(f"{dist}.distance")
        cmds.connectAttr(f'{self.stretch_jnt_chain[0]}.worldMatrix[0]', f'{dist}.inMatrix1')
        cmds.connectAttr(f'{self.ctl}.worldMatrix[0]', f'{dist}.inMatrix2')

        div = cmds.createNode("multiplyDivide", n=f"{self.ctl}_md")
        cmds.setAttr(f"{div}.operation", 2)
        cmds.connectAttr(f"{dist}.distance", f"{div}.input1X")
        cmds.setAttr(f"{div}.input2X", max_dist)

        axis = ["X", "Y", "Z"]
        channels = ["R", "G", "B"]
        blend_nodes = []
        for jnt_stretch, index in zip(self.stretch_jnt_chain[1:], range(0, len(self.stretch_jnt_chain[1:]))) :
            jnt = self.jnts[index + 1]
            mult = cmds.createNode("multDoubleLinear", n=f"{jnt_stretch}_mdl")
            cmds.connectAttr(f"{div}.outputX", f"{mult}.input1")
            cmds.setAttr(f"{mult}.input2", cmds.getAttr(f"{jnt_stretch}.translateX"))

            if index % 3 == 0:  # create a condition node every 3 jnt_stretch because it only has 3 inputs slots
                blend = cmds.createNode("blendColors", n=f"{self.ctl}_bc_{index // 3}")
                cmds.setAttr(f"{blend}.blender", 1)
                condition = cmds.createNode("condition", n=f"{self.ctl}_cond_{index // 3}")
                cmds.connectAttr(f"{dist}.distance", f"{condition}.firstTerm")
                cmds.connectAttr(f"{blend}.output", f"{condition}.colorIfTrue")
            else:
                blend = f"{self.ctl}_bc_{index // 3}"
                condition = f"{self.ctl}_cond_{index // 3}"

            cmds.connectAttr(f"{jnt_stretch}.translateX", f"{blend}.color2{channels[index % 3]}")
            cmds.connectAttr(f"{mult}.output", f"{blend}.color1{channels[index % 3]}")
            cmds.setAttr(f"{condition}.secondTerm", max_dist)
            cmds.setAttr(f"{condition}.operation", 2)
            cmds.setAttr(f"{condition}.colorIfFalse{channels[index % 3]}", cmds.getAttr(f"{jnt_stretch}.translateX"))

            cmds.connectAttr(f"{condition}.outColor{channels[index % 3]}", f"{jnt}.translateX")
            blend_nodes.append(blend)
        if self.ctl_root:
            cmds.pointConstraint(self.ctl_root, self.stretch_jnt_chain[0], mo=False)
        return blend_nodes


class IkFkLimb(Limb):
    """
    A IkFkLimb component contains :
        - an IkLimb component
        - an FkLimb component
        - a joint chain that blends between ik and fk joint chain
        - a parameter ctl to switch
    """

    MODULE_TYPE = ComponentType.IK_FK_LIMB

    IK_FK_SUFFIX = "_blend_IK_FK"

    CTL_IK_FK_COLOR = "blue"
    CTL_IK_FK_SHAPE = "double arrow"

    LOCK_SUFFIX = "_lock"

    def __init__(self, jnt_list: list[str], name=None, config: Config=None):
        super().__init__(jnt_list=jnt_list, name=name, duplicate_jnt=True, suffix=self.IK_FK_SUFFIX, config=config)

        self.fk_limb = FkLimb(jnt_list, config=config)
        self.ik_limb = IkLimb(jnt_list, pole_vector=True, config=config)

        self._build_ik_fk(jnt_list)

    def _build_ik_fk(self, jnt_list: list[str]):
        self.parameter_ctl = Controller(jnt_list[0] + self.IK_FK_SUFFIX)
        pos = cmds.xform(jnt_list[0], q=1, ws=1, t=1)
        self.parameter_ctl.pos = [pos[0], pos[1] + 2 * self.SCALE, pos[2]]
        self.parameter_ctl.shape = self.CTL_IK_FK_SHAPE
        self.parameter_ctl.shape_scale = self.SCALE * 0.5
        self.parameter_ctl.color = self.CTL_IK_FK_COLOR
        cmds.rotate(0, 0, 90, self.parameter_ctl.cvs, os=1, r=1)
        self._ctl_chain = [self.parameter_ctl]

        add_separator_attribute(self.parameter_ctl.name, separator_name="Edit_Limb" )

        lock_attributes(self.parameter_ctl.name, attr_name="all")
        cmds.addAttr(self.parameter_ctl.name, ln=self.IK_FK_SUFFIX, at="float", keyable=1, min=0, max=1, dv=0)

        for joint_IK, joint_FK, joint_blend in zip(self.ik_limb.jnts, self.fk_limb.jnts, self.jnts):
            # create rotate pair_blend
            pair_blend = cmds.createNode("pairBlend", name=f'{joint_blend}_pb')

            # connect rotates to pair_blend
            cmds.connectAttr(f'{joint_FK}.rotate', f'{pair_blend}.inRotate1')
            cmds.connectAttr(f'{joint_IK}.rotate', f'{pair_blend}.inRotate2')
            cmds.connectAttr(f'{pair_blend}.outRotate', f'{joint_blend}.rotate')

            # connect switch attribute to pair_blend weight
            cmds.connectAttr(f'{self.parameter_ctl}.{self.IK_FK_SUFFIX}', f'{pair_blend}.weight')

            # create translate blend color
            blend_colors = cmds.createNode("blendColors", name=f'{joint_blend}_bc')

            # connect translates to pair_blend
            cmds.connectAttr(f'{joint_FK}.translate', f'{blend_colors}.color2')
            cmds.connectAttr(f'{joint_IK}.translate', f'{blend_colors}.color1')
            cmds.connectAttr(f'{blend_colors}.output', f'{joint_blend}.translate')

            # connect switch attribute to pair_blend weight
            cmds.connectAttr(f'{self.parameter_ctl}.{self.IK_FK_SUFFIX}', f'{blend_colors}.blender')

        # connect switch attribute to visibility
        cmds.connectAttr(f'{self.parameter_ctl}.{self.IK_FK_SUFFIX}', f'{self.ik_limb.ctl_grp_name}.visibility')

        self.reverse = cmds.createNode("reverse", name=f'{jnt_list[0]}_rev')
        cmds.connectAttr(f'{self.parameter_ctl}.{self.IK_FK_SUFFIX}', f"{self.reverse}.inputX")
        cmds.connectAttr(f"{self.reverse}.outputX", f'{self.fk_limb.ctl_grp_name}.visibility')

        # set ik and fk joints visibility to 0
        cmds.setAttr(f'{self.ik_limb.jnt_grp}.visibility', 0)
        cmds.setAttr(f'{self.fk_limb.jnt_grp}.visibility', 0)

        self.ctl_grp_name = cmds.group(self._ctl_chain[0].zro_grp_name, name=self._ctl_chain[0].name + self.GROUP_SUFFIX)

    def build_bendy(self,
            flc_on_u=None,
            flc_on_v=1,

            flc_param_u_start=0,
            flc_param_u_end=1,
            flc_param_u_offset=0,

            flc_param_v_start=0,
            flc_param_v_end=1,
            flc_param_v_offset=0
            ):
        super().build_bendy(
            flc_on_u=flc_on_u,
            flc_on_v=flc_on_v,

            flc_param_u_start=flc_param_u_start,
            flc_param_u_end=flc_param_u_end,
            flc_param_u_offset=flc_param_u_offset,

            flc_param_v_start=flc_param_v_start,
            flc_param_v_end=flc_param_v_end,
            flc_param_v_offset=flc_param_v_offset
            )

        cmds.addAttr(self.parameter_ctl.name,
                     ln="bendy_" + self.ctl.CONTROLLER_PREFIX + "visibility", at="float", keyable=1,
                     min=0, max=1, dv=0)
        for ctl in self.offset_ctl_chain:
            cmds.connectAttr(
                f'{self.parameter_ctl.name}.{"bendy_" + self.ctl.CONTROLLER_PREFIX + "visibility"}',
                f'{ctl.zro_grp_name}.visibility')

        cmds.addAttr(self.parameter_ctl.name, ln=self.CTL_BENDY_SUFFIX + "_" + self.ctl.CONTROLLER_PREFIX + "visibility", at="float", keyable=1, min=0, max=1, dv=0)
        cmds.connectAttr(f'{self.parameter_ctl.name}.{self.CTL_BENDY_SUFFIX + "_" + self.ctl.CONTROLLER_PREFIX + "visibility"}', f'{self.ribbon.flc_grp_name}.visibility')

        self.build_lock_elbow()

    def build_lock_elbow(self):
        """
        Create a lock elbow behavior for this bendy Ik Fk Limb
        """
        if not self._is_bendy:
            return
        if not len(self._jnt_chain) == 3:
            return

        cmds.addAttr(self.parameter_ctl.name, ln=self.LOCK_SUFFIX, at="float", keyable=1, min=0, max=1, dv=0)

        # nodes setup
        pole = self.ik_limb.ctl_pole
        ctl_mid = self.offset_ctl_chain[2]
        blend = cmds.createNode("blendMatrix", n=f'{pole}{self.LOCK_SUFFIX}_bm')
        mult = cmds.createNode("multMatrix", n=f'{pole}{self.LOCK_SUFFIX}_mm')
        decompose = cmds.createNode("decomposeMatrix", n=f'{pole}{self.LOCK_SUFFIX}_dcm')

        # Connect point matrix constraint
        cmds.connectAttr(f'{self.parameter_ctl.name}.{self.LOCK_SUFFIX}', f'{blend}.target[0].weight', f=1)
        cmds.connectAttr(f'{pole}.worldMatrix[0]', f'{blend}.target[0].targetMatrix', f=1)
        cmds.connectAttr(f'{ctl_mid.zro_grp_name}.parentMatrix[0]', f'{blend}.inputMatrix', f=1)

        cmds.connectAttr(f'{blend}.outputMatrix', f'{mult}.matrixIn[0]', f=1)
        cmds.connectAttr(f'{ctl_mid.zro_grp_name}.parentInverseMatrix', f'{mult}.matrixIn[1]', f=1)

        cmds.connectAttr(f'{mult}.matrixSum', f'{decompose}.inputMatrix', f=1)
        cmds.connectAttr(f'{decompose}.outputTranslate', f'{ctl_mid.zro_grp_name}.translate', f=1)

    def build_root_ctl(self) -> Controller:
        ctl = super().build_root_ctl()

        cmds.pointConstraint(ctl, self.ik_limb.jnts[0], mo=True)
        cmds.pointConstraint(ctl, self.jnts[0], mo=True)

        cmds.parent(self.fk_limb.ctl_grp_name, ctl)
        cmds.parent(self.ik_limb.ctl_grp_name, ctl)

        cmds.addAttr(self.parameter_ctl.name, ln=self.CTL_ROOT_SUFFIX + "_visibility", at="float", keyable=1, min=0, max=1, dv=0)
        cmds.connectAttr(f'{self.parameter_ctl.name}.{self.CTL_ROOT_SUFFIX + "_visibility"}', f'{self.ctl_root.shape}.visibility')

        return ctl

    def build_stretchy(self):
        """
        Same as IkLimb build_stretchy but now you can set the weight of stretching with self.ctl_param's attribute
        """
        attr_blend = self.ik_limb.IK_SUFFIX + self.ik_limb.STRETCH_SUFFIX
        cmds.addAttr(self.parameter_ctl.name, ln=attr_blend, at="float", keyable=1, min=0, max=1, dv=0)

        blend_nodes = self.ik_limb.build_stretchy()
        for node in blend_nodes:
            cmds.connectAttr(f"{self.parameter_ctl.name}.{attr_blend}", f"{node}.blender", f=1)

