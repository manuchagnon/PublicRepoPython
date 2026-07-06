from maya import cmds

from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.component.base import ComponentType
from devMaya.auto_rig.component.composed import ComposedComponent
from devMaya.auto_rig.component.controller import ControllerShapes, Controller
from devUi.utils.colors import Colors
from devMaya.auto_rig.component.ribbon import LimbRibbon
from devMaya.utils.api import (rotate_ctl,
                               lock_attributes,
                               get_pole_vector_placement,
                               create_annotation,
                               add_separator_attribute,
                               create_crv_with_obj_list,
                               determine_component_name,
                               connect_attributes,
                               set_jnt_color,
                               create_jnt_chain_blending,
                               hinge_constraint,
                               Attribute, Separator,
                               )


class Limb(ComposedComponent):
    """
    A Limb module contains :
        - a joint chain, must be well oriented at the beginning
        - a joint group
    Methods :
        - add offset controller and joint
    """

    TYPE = ComponentType.LIMB

    CTL_BENDY_COLOR : Colors | str = "red"
    CTL_BENDY_SHAPE = "round square"
    CTL_BENDY_SUFFIX = "_offset"

    CTL_ROOT_COLOR : Colors | str = "pink"
    CTL_ROOT_SHAPE = "box"
    CTL_ROOT_SUFFIX = "_root"

    CTL_OFFSET_DENSITY = 3

    HINGE_SUFFIX = "_hinge"

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
        # self._ctl_chain.insert(0, ctl)

        return ctl

    def create_param_for_root_ctl(self, ctl_param : Controller | None = None):
        """
        Used after creating ctl_root on the limb to hold attributes for visibility
        """
        if not self.ctl_root:
            print("First build root ctl before creating parameter attributes")
            return

        if not ctl_param:
            ctl_param = self.ctl_param

        attr = Attribute(self.CTL_ROOT_SUFFIX + "_visibility",
                         type = "float", keyable = 1, min = 0, max = 1, default_value=0
        )
        attr.add_to_node(ctl_param.name)
        attr.plug_to(f"{self.ctl_root.shape}.visibility")

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

    def create_param_for_offset_ctl(self, ctl_param : Controller | None = None):
        """
        Used after creating offset_ctl on the limb to hold attributes for visibility
        """
        if not self._has_offset_jnt:
            print("First build offset ctl before creating parameter attributes")
            return

        if not ctl_param:
            ctl_param = self.ctl_param

        attr = Attribute("bendy_" + self.ctl.CONTROLLER_PREFIX + "visibility",
                         type = "float", keyable = 1, min = 0, max = 1, default_value=0
        )
        attr.add_to_node(ctl_param.name)
        for ctl in self.offset_ctl_chain:
            attr.plug_to(f"{ctl.zro_grp_name}.visibility")

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
            maximumInfluences=3,
            dropoffRate= 10,
            obeyMaxInfluences=1
        )

    def create_param_for_bendy(self, ctl_param : Controller | None = None):
        """
        Used after creating bendy setup on the limb to hold attributes for visibility
        """
        if not self._is_bendy:
            print("First build bendy before creating parameter attributes")
            return

        if not ctl_param:
            ctl_param = self.ctl_param
        attr = Attribute(self.CTL_BENDY_SUFFIX + "_" + self.ctl.CONTROLLER_PREFIX + "visibility",
                         type = "float", keyable = 1, min = 0, max = 1, default_value=0
        )
        attr.add_to_node(ctl_param.name)
        attr.plug_to(f"{self.ribbon.flc_grp_name}.visibility")

    def build_hinge(self, orient_source:str, ctl_root: Controller | None = None, ctl_param : Controller | None = None):
        """
        Create a hinge setup (orient constraint) to make the limb keep its orientation
        """
        if not self.ctl_root:
            print("Cannot create hinge setup, you have to build_root() first")
            return

        if not ctl_param:
            ctl_param = self.ctl_param

        if not ctl_root:
            ctl_root = self.ctl_root

        hinge_constraint(orient_source=orient_source,
                         orient_target=ctl_root,
                         ctl_blend=ctl_param,
                         lct_name=self.LOCATOR_PREFIX + ctl_param.name + self.HINGE_SUFFIX,
                         lct_parent=ctl_root.zro_grp_name,
                         suffix=self.HINGE_SUFFIX)

    def build_maintain_volume_setup(self):
        """
        Create a setup to fake maintaining volume on limb's ribbon joints
        It uses the distance between bendy controllers to remap the scale Y and Z of joints
        It is added to offset ctl scale
        TO DO
        """
        return
        if not self._is_bendy:
            print("Cannot create maintain volume setup, you have to build_bendy() first")
            return

        # self.offset_ctl_chain

        # self.ribbon.ctls

        # self.ribbon.jnts

        amount = len(self.ribbon.ctls)
        print(amount)

        jnt_density = self.CTL_OFFSET_DENSITY
        previous_index = -1

        angles_amount = len(self.offset_ctl_chain)//3
        print("how many angles", amount)
        for angle_index in range(angles_amount):

            print("- angle index:", angle_index)
            affected_ctls = [self.ribbon.ctls[i] for i in range(angle_index, angle_index+3)]
            print("- affected ctls:", affected_ctls)

            for i, (jnt, ctl) in enumerate(zip(self.ribbon.jnts, self.ribbon.ctls)):
                ctl_bendy_index = i // jnt_density
                ctl_bendy_start = self.offset_ctl_chain[ctl_bendy_index]
                ctl_bendy_mid = self.offset_ctl_chain[ctl_bendy_index + 1]
                ctl_bendy_end = self.offset_ctl_chain[ctl_bendy_index + 2]


                if ctl_bendy_index != previous_index:
                    dist = cmds.createNode("distanceBetween", name=f"dist_{ctl_bendy_start}")
                    cmds.connectAttr(f"{ctl_bendy_start}.worldMatrix[0]", f"{dist}.inMatrix1", f=1)
                    cmds.connectAttr(f"{ctl_bendy_end}.worldMatrix[0]", f"{dist}.inMatrix2", f=1)
                    distance = cmds.getAttr(f"{dist}.distance")

                    previous_index = ctl_bendy_index



                print(" - ", i, ctl, jnt, ", start end :", ctl_bendy_start, ctl_bendy_end)

    @property
    def jnts(self):
        if self._has_offset_jnt:
            if self._is_bendy and False:
                # using ribbon's jnt for constraining the output was not good with rotations
                # so i removed this way of getting ribbon's jnts
                # instead use self.ribbon.jnts
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

    def bind_jnts(self) -> list[str]:
        if self._has_offset_jnt:
            if self._is_bendy:
                return self.ribbon.jnts
            else:
                return self._offset_jnt_chain
        else:
            return self._jnt_chain


class FkLimb(Limb):
    """
    A FkLimb module contains :
        - a joint chain
        - a ctl group
        - a FK ctl chain
    """

    TYPE : ComponentType = ComponentType.FK_LIMB

    FK_SUFFIX : str = "_FK"
    CTL_FK_COLOR : Colors | str = "green"
    CTL_FK_SHAPE : ControllerShapes | str = "circle"

    CORRECTIVE_SUFFIX : str = "_corrective"
    CORRECTIVE_TRANSLATE_MULTIPLIER = 1.0

    def __init__(self, jnt_list:  list[str], name=None, duplicate_jnt=True, config: Config=None):

        if jnt_list == []:
            self._ctl_chain = []
            self.ctl_grp_name = None
            cmds.error("Empty FK limb")
            return

        # duplicate the joint chain with '_FK' suffix and store it
        super().__init__(jnt_list, duplicate_jnt=duplicate_jnt, name=name, suffix=self.FK_SUFFIX, config=config)

        ctl_chain = [
            Controller.CONTROLLER_PREFIX + jnt.split(self.JOINT_PREFIX, 1)[-1]
            for jnt in self.jnts
        ]

        self.corrective_jnt_index = 0
        self.CORRECTIVE_TRANSLATE_MULTIPLIER *= self.SCALE

        # if ctl already exist
        if all([cmds.objExists(ctl) for ctl in ctl_chain]):
            self.build_from_scene_data(self.jnts)
        else:
            self._build()

    def _build(self):
        """
        Build the FK limb by creating Fk ctl on the jnt chain and store them in self._ctl_chain
        """
        self._ctl_chain = []
        for jnt in self.jnts:
            ctl = Controller(jnt)
            ctl.shape = self.CTL_FK_SHAPE
            ctl.shape_scale = self.SCALE
            ctl.color = self.CTL_FK_COLOR
            ctl.pos = cmds.xform(jnt, q=1, ws=1, t=1)
            ctl.rot = cmds.xform(jnt, q=1, ws=1, ro=1)
            ctl.shape_rot = [0, 0, 90]
            # rotate_ctl(ctl, "Z", 90)
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

    def build_dynamic(self):
        """
        TO DO
        Create a dynamic setup with follicle and nucleus to obtain overshoot effect on top of FK Limb
        """
        return
        crv = create_crv_with_obj_list(self.jnts)

        jnt_chain_dynamic = self._duplicate_jnt_chain(self.jnts, suffix="_dynamic")

        dyna = cmds.mel.eval(f"makeCurvesDynamic(crv, 2, {'1', '0', '1', '1', '0'})")
        print("DYNA =", dyna)

    def build_quick_rotation_setup(
            self,
            ctl_target_rotation : Controller,
            axes_match : tuple[tuple[float,str]] | None = None
            ) -> list[str]:
        """
        Create 'ROT' offset grp on every ctl and connect rotate
        axes_match is used to connect xyz axes from ctl_target_rotation to +x,-x,+y,-y,+z,-z of 'ROT' offset grp,
        with multiplier float value
        axes_match must be constructed as ((1.0,"X"), (1.0,"Y"), (1.0,"Z"))
        """
        rot_grps = self.add_offset_grp_on_ctl(suffix="ROT")
        for rot_grp in rot_grps:
            if not axes_match:
                # Classic connexions
                connect_attributes(ctl_target_rotation, rot_grp, attributes_list=["rotate"])
            else:
                # Custom connexions
                for axis_src, (multiplier, axis_dst) in zip(self.AXES, axes_match):
                    if multiplier == 1.0:
                        cmds.connectAttr(f"{ctl_target_rotation}.rotate{axis_src}", f"{rot_grp}.rotate{axis_dst}")
                    else:
                        mult = cmds.createNode("multDoubleLinear", name="mult_" + rot_grp)
                        cmds.connectAttr(f"{ctl_target_rotation}.rotate{axis_src}", f"{mult}.input1")
                        cmds.setAttr(f"{mult}.input2", multiplier)
                        cmds.connectAttr(f"{mult}.output", f"{rot_grp}.rotate{axis_dst}")
        return rot_grps

    def build_corrective_jnts_setup(self, rot_axis="Z", trans_axis="Y"):
        """
        Create a corrective joint setup for each joint of the chain
        """
        cmds.select(clear=True)

        # store index in case the limb has multiple corrective joint setups
        self.corrective_jnt_index += 1
        index = str(self.corrective_jnt_index)

        # get the direction of the corrective joint setup
        if "-" in rot_axis:
            rot_axis = rot_axis[1:]
            rot_orient = -1
        else:
            rot_orient = 1
        if "-" in trans_axis:
            trans_axis = trans_axis[1:]
            trans_orient = -1
        else:
            trans_orient = 1

        for ctl, jnt in zip(self.ctls, self.jnts):
            jnt_start = cmds.joint(name=jnt + self.CORRECTIVE_SUFFIX +index + rot_axis + "_start")
            cmds.setAttr(f"{jnt_start}.radius", 0.5)
            set_jnt_color(jnt_start, "yellow")
            jnt_end = cmds.joint(name=jnt + self.CORRECTIVE_SUFFIX +index + rot_axis +  "_end")
            cmds.setAttr(f"{jnt_end}.radius", 0.5)
            set_jnt_color(jnt_end, "yellow")
            cmds.select(clear=True)
            cmds.matchTransform(jnt_start, jnt, pos=True, rot=True)
            cmds.parent(jnt_start, jnt)
            cmds.makeIdentity(jnt_start, apply=True)

            # Attributes
            separator = Separator(node=ctl, separator_name=self.CORRECTIVE_SUFFIX + self.JOINT_PREFIX + index)
            separator.add_to_node(ctl)
            attr_jnt_r_dv = 45.0 * rot_orient
            attr_jnt_r = Attribute(node=ctl, add_to_node=True, long_name=self.CORRECTIVE_SUFFIX + self.JOINT_PREFIX + index+ "_rotate", type="float", default_value=attr_jnt_r_dv)
            attr_jnt_t_min_dv = self.SCALE * self.CORRECTIVE_TRANSLATE_MULTIPLIER * trans_orient
            attr_jnt_t_min = Attribute(node=ctl, add_to_node=True,  long_name=self.CORRECTIVE_SUFFIX + self.JOINT_PREFIX + index+ "_translate_min", type="float", default_value=attr_jnt_t_min_dv)
            attr_jnt_t_max_dv = self.SCALE * self.CORRECTIVE_TRANSLATE_MULTIPLIER * 1.5 * trans_orient
            attr_jnt_t_max = Attribute(node=ctl, add_to_node=True,  long_name=self.CORRECTIVE_SUFFIX + self.JOINT_PREFIX + index+ "_translate_max", type="float", default_value=attr_jnt_t_max_dv)
            attr_ctl_r_max_dv = 90 * rot_orient
            attr_ctl_r_max = Attribute(node=ctl, add_to_node=True,  long_name=Controller.CONTROLLER_PREFIX +index+ "rotate_max", type="float", default_value=attr_ctl_r_max_dv)
            attr_ctl_r_min = Attribute(node=ctl, add_to_node=True,  long_name=Controller.CONTROLLER_PREFIX +index+ "rotate_min", type="float", default_value=-attr_ctl_r_max_dv)

            # Remap
            remap_translate = cmds.createNode("remapValue", name="remap_translate" + jnt + self.CORRECTIVE_SUFFIX)
            cmds.connectAttr(f"{jnt}.rotate{rot_axis}", f"{remap_translate}.inputValue")
            attr_jnt_t_max.plug_to(f"{remap_translate}.outputMin")
            attr_jnt_t_min.plug_to(f"{remap_translate}.outputMax")
            attr_ctl_r_min.plug_to(f"{remap_translate}.inputMin")
            attr_ctl_r_max.plug_to(f"{remap_translate}.inputMax")
            cmds.connectAttr(f"{remap_translate}.outValue", f"{jnt_end}.translate{trans_axis}")

            remap_rotate = cmds.createNode("remapValue", name="remap_rotate" + jnt + self.CORRECTIVE_SUFFIX)
            cmds.connectAttr(f"{jnt}.rotate{rot_axis}", f"{remap_rotate}.inputValue")
            attr_ctl_r_min.plug_to(f"{remap_rotate}.inputMin")
            attr_ctl_r_max.plug_to(f"{remap_rotate}.inputMax")
            attr_jnt_r.plug_to(f"{remap_rotate}.outputMin")

            # Multiply
            mult = cmds.createNode("multDoubleLinear", name="mult_" + jnt + self.CORRECTIVE_SUFFIX)
            cmds.setAttr(f"{mult}.input2", -1)
            attr_jnt_r.plug_to(f"{mult}.input1")
            cmds.connectAttr(f"{mult}.output", f"{remap_rotate}.outputMax")
            cmds.connectAttr(f"{remap_rotate}.outValue", f"{jnt_start}.rotate{rot_axis}")


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

    TYPE : ComponentType = ComponentType.IK_LIMB

    IK_SUFFIX : str = "_IK"
    POLE_VECTOR_SUFFIX : str = "_pole_vector"
    POLE_VECTOR_DISTANCE : float = 8.0
    IK_HANDLE_SUFFIX : str = "_ik_handle"

    CTL_IK_COLOR : Colors | str = "red"
    CTL_IK_SHAPE : ControllerShapes | str = "box"
    CTL_IK_SCALE : float = 1.3

    CTL_POLE_SHAPE : ControllerShapes | str = "sphere"

    STRETCH_SUFFIX : str = "_stretch"

    def __init__(self, jnt_list: list[str], name=None, pole_vector=False, stretchy=False, duplicate_jnt=True, config: Config=None):

        if jnt_list == []:
            self._ctl_chain = []
            self.ctl_grp_name = None
            self.ik_handle = None
            cmds.error("Empty IK limb")
            return

        # duplicate the joint chain with '_IK' suffix and store it
        super().__init__(jnt_list, duplicate_jnt=duplicate_jnt, name=name, suffix=self.IK_SUFFIX, config=config)
        self.stretch_jnt_chain = []

        if cmds.objExists(Controller.CONTROLLER_PREFIX + jnt_list[-1] + self.IK_SUFFIX):
            self.build_from_scene_data(self.jnts)
        else:
            self._build()

        if pole_vector:
            self.build_pole_vector()
        if stretchy:
            self.build_stretchy()

    # -- Builders

    def _build(self):
        """
        Build the IK limb by creating Ik ctl on the last jnt and store it in self._ctl_chain
        """

        ctl = Controller(self.jnts[-1])
        ctl.shape = self.CTL_IK_SHAPE
        ctl.shape_scale = self.SCALE * self.CTL_IK_SCALE
        ctl.color = self.CTL_IK_COLOR
        ctl.pos = cmds.xform(self.jnts[-1], q=1, ws=1, t=1)
        ctl.rot = cmds.xform(self.jnts[-1], q=1, ws=1, ro=1)

        # cmds.connectAttr(f"{ctl}.rotate", f"{self.jnts[-1]}.rotate")
        cmds.orientConstraint(ctl.name, self.jnts[-1])

        self.ik_handle = cmds.ikHandle(name=ctl.name + self.IK_HANDLE_SUFFIX,
                                  startJoint=self.jnts[0],
                                  endEffector=self.jnts[-1],
                                  solver='ikRPsolver')[0]

        cmds.parent(self.ik_handle, ctl) # Convert parenting into a matrix constraint
        # cmds.connectAttr(f"{ctl}.worldMatrix[0]", f"{self.ik_handle}.offsetParentMatrix")

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
        cmds.connectAttr(f'{self.stretch_jnt_chain[0]}.worldMatrix[0]', f'{dist}.inMatrix1', f=1)
        cmds.connectAttr(f'{self.ctl}.worldMatrix[0]', f'{dist}.inMatrix2', f=1)

        div = cmds.createNode("multiplyDivide", n=f"{self.ctl}_md")
        cmds.setAttr(f"{div}.operation", 2)
        cmds.connectAttr(f"{dist}.distance", f"{div}.input1X", f=1)
        cmds.setAttr(f"{div}.input2X", max_dist)

        axis = ["X", "Y", "Z"]
        channels = ["R", "G", "B"]
        blend_nodes = []
        for jnt_stretch, index in zip(self.stretch_jnt_chain[1:], range(0, len(self.stretch_jnt_chain[1:]))) :
            jnt = self.jnts[index + 1]
            mult = cmds.createNode("multDoubleLinear", n=f"{jnt_stretch}_mdl")
            cmds.connectAttr(f"{div}.outputX", f"{mult}.input1", f=1)
            cmds.setAttr(f"{mult}.input2", cmds.getAttr(f"{jnt_stretch}.translateX"))

            if index % 3 == 0:  # create a condition node every 3 jnt_stretch because it only has 3 inputs slots
                blend = cmds.createNode("blendColors", n=f"{self.ctl}_bc_{index // 3}")
                cmds.setAttr(f"{blend}.blender", 1)
                condition = cmds.createNode("condition", n=f"{self.ctl}_cond_{index // 3}")
                cmds.connectAttr(f"{dist}.distance", f"{condition}.firstTerm", f=1)
                cmds.connectAttr(f"{blend}.output", f"{condition}.colorIfTrue", f=1)
            else:
                blend = f"{self.ctl}_bc_{index // 3}"
                condition = f"{self.ctl}_cond_{index // 3}"

            cmds.connectAttr(f"{jnt_stretch}.translateX", f"{blend}.color2{channels[index % 3]}", f=1)
            cmds.connectAttr(f"{mult}.output", f"{blend}.color1{channels[index % 3]}", f=1)
            cmds.setAttr(f"{condition}.secondTerm", max_dist)
            cmds.setAttr(f"{condition}.operation", 2)
            cmds.setAttr(f"{condition}.colorIfFalse{channels[index % 3]}", cmds.getAttr(f"{jnt_stretch}.translateX"))

            cmds.connectAttr(f"{condition}.outColor{channels[index % 3]}", f"{jnt}.translateX", f=1)
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
        - a ctl_param to switch
    """

    MODULE_TYPE : ComponentType = ComponentType.IK_FK_LIMB

    IK_FK_SUFFIX : str = "_blend"
    CTL_PARAMETER_SUFFIX : str = IK_FK_SUFFIX

    LOCK_SUFFIX : str = "_lock"

    def __init__(self, jnt_list: list[str], name=None, config: Config=None):
        super().__init__(jnt_list=jnt_list, name=name, duplicate_jnt=True, suffix=self.IK_FK_SUFFIX, config=config)

        self.fk_limb = FkLimb(self.jnts, config=config)
        self.ik_limb = IkLimb(self.jnts, pole_vector=True, config=config)

        self._build_ik_fk()

    def _build_ik_fk(self):

        # ctl_param
        self.build_ctl_param(name=self.jnts[0])
        pos = cmds.xform(self.jnts[0], q=1, ws=1, t=1)
        self.ctl_param.pos = [pos[0], pos[1] + 1.7 * self.SCALE, pos[2]]
        self.ctl_param.shape_rot = [90, 0, 90]

        self._ctl_chain = [self.ctl_param]

        add_separator_attribute(self.ctl_param.name, separator_name="Edit_Limb")

        switch_attr = Attribute(self.IK_FK_SUFFIX, type="float", keyable=1, min=0.0, max=1.0, default_value=0.0)
        switch_attr.add_to_node(self.ctl_param.name)

        create_jnt_chain_blending(
            jnt_chain_parent_1=self.ik_limb.jnts,
            jnt_chain_parent_2=self.fk_limb.jnts,
            jnt_chain_target=self.jnts,
            attribute_blender=switch_attr)

        # connect switch attribute to visibility
        switch_attr.plug_to(f'{self.ik_limb.ctl_grp_name}.visibility')

        reverse = cmds.createNode("reverse", name=f'{self.jnts[0]}_rev')
        switch_attr.plug_to(f"{reverse}.inputX")
        cmds.connectAttr(f"{reverse}.outputX", f'{self.fk_limb.ctl_grp_name}.visibility')

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
        self.create_param_for_offset_ctl()

        self.create_param_for_bendy()

        # self.build_lock_elbow()

    def build_lock_elbow(self):
        """
        Create a lock elbow behavior for this bendy Ik Fk Limb
        """
        if not self._is_bendy:
            return
        if not len(self._jnt_chain) == 3:
            return

        cmds.addAttr(self.ctl_param.name, ln=self.LOCK_SUFFIX, at="float", keyable=1, min=0, max=1, dv=0)

        # nodes setup
        pole = self.ik_limb.ctl_pole
        ctl_mid = self.offset_ctl_chain[2]
        blend = cmds.createNode("blendMatrix", n=f'{pole}{self.LOCK_SUFFIX}_bm')
        mult = cmds.createNode("multMatrix", n=f'{pole}{self.LOCK_SUFFIX}_mm')
        decompose = cmds.createNode("decomposeMatrix", n=f'{pole}{self.LOCK_SUFFIX}_dcm')

        # Connect point matrix constraint
        cmds.connectAttr(f'{self.ctl_param.name}.{self.LOCK_SUFFIX}', f'{blend}.target[0].weight', f=1)
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

        self.create_param_for_root_ctl()

        return ctl

    def build_stretchy(self):
        """
        Same as IkLimb build_stretchy but now you can set the weight of stretching with self.ctl_param's attribute
        """
        attr_blend = self.ik_limb.IK_SUFFIX + self.ik_limb.STRETCH_SUFFIX
        cmds.addAttr(self.ctl_param.name, ln=attr_blend, at="float", keyable=1, min=0, max=1, dv=0)

        blend_nodes = self.ik_limb.build_stretchy()
        for node in blend_nodes:
            cmds.connectAttr(f"{self.ctl_param.name}.{attr_blend}", f"{node}.blender", f=1)

    def ik_handle(self):
        return self.ik_limb.ik_handle

    def toggle_if_fk_switch(self):
        """
        Switch between fk and ik state with the API
        """
        attr = f"{self.ctl_param}.{self.IK_FK_SUFFIX}"
        switch = cmds.getAttr(attr)
        cmds.setAttr(attr, not switch)

    def set_ik_fk_switch(self, switch: int | bool):
        """
        Set the switch between fk and ik state with the API
        """
        attr = f"{self.ctl_param}.{self.IK_FK_SUFFIX}"
        cmds.setAttr(attr, switch)
