from maya import cmds


from devMaya.utils.api import (
    aim_matrix_constraint,
    create_decompose_matrix_node,

    create_crv_with_obj_list,
    distribute_lct_on_crv,
    create_crv_with_pos_list,
    create_set,

    add_separator_attribute,
)
from devMaya.auto_rig.component.controller import Controller
from devUtils.maths import logistic_interpolation

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.configs.config import Config

class Eye(BaseModule):

    """
    Eye module for stylized characters

    Only works for spherical eyes currently

    Requires :
    - all vtx from the up eyelid
    - all vtx from the down eyelid
    - the joint at the center of the spherical eye
    """


    TYPE = ModuleType.EYE

    UP_SUFFIX = "_up"
    DOWN_SUFFIX = "_dw"
    BLINK_SUFFIX = "_blink"

    CTL_PER_EYE_LID = 7
    CURVE_HIGH_SUFFIX = "_high"
    CURVE_LOW_SUFFIX = "_low"

    WIRE_DEFORMER_PREFIX = "wire_"
    SOCKET_SUFFIX = "_socket"

    CTL_MAIN_SHAPE = "box"
    CTL_MAIN_COLOR = "red"
    CTL_ORIENT_COLOR = "red"
    CTL_EYELID_SHAPE = "circle"
    CTL_EYELID_COLOR = "yellow"


    def __init__(self, vtx_eyelid_up: list[str] | str, vtx_eyelid_down: list[str] | str, jnt_eye_center:str, name:str=None, config:Config=None):
        super().__init__(name=name, config=config)

        self.jnt_center = jnt_eye_center

        if ":" in vtx_eyelid_up:
            self.vtx_eyelid_up : list[str] = cmds.ls(vtx_eyelid_up, flatten=True)
        else:
            self.vtx_eyelid_up : list[str] = vtx_eyelid_up

        if ":" in vtx_eyelid_down:
            self.vtx_eyelid_dw : list[str] = cmds.ls(vtx_eyelid_down, flatten=True)
        else:
            self.vtx_eyelid_dw : list[str] = vtx_eyelid_down

        self.crv_high = []
        self.crv_low = []
        self._ctls = []
        self.ctl_main = None
        self.ctl_orient = None

        self.bind_jnts : list[str] = []

    def build(self):
        dont_touch_list = []
        jnt_center_pos = cmds.xform(self.jnt_center, q=1, ws=1, t=1)
        jnt_center_rot = cmds.xform(self.jnt_center, q=1, ws=1, ro=1)

        ctl_main = Controller(name=self.name + self.BLINK_SUFFIX)
        ctl_main.pos = jnt_center_pos
        ctl_main.rot = jnt_center_rot
        ctl_main.color = self.CTL_MAIN_COLOR
        ctl_main.shape = self.CTL_MAIN_SHAPE
        ctl_main.shape_scale  =self.SCALE * 10
        ctl_main.shape_pos = [0, 0, -self.SCALE*40]
        self.ctl_main = ctl_main
        self._ctl_chain = [ctl_main]

        cmds.select(clear=1)
        jnt_socket = cmds.joint(name=self.jnt_center + self.SOCKET_SUFFIX, position=jnt_center_pos)
        cmds.select(clear=1)
        cmds.xform(jnt_socket, ws=1, ro=jnt_center_rot)
        cmds.parent(self.jnt_center, jnt_socket)
        cmds.parent(jnt_socket, self.ctl_main)

        ctl_orient = Controller(name=self.name)
        ctl_orient.pos = jnt_center_pos
        ctl_orient.rot = jnt_center_rot
        ctl_orient.shape_rot = [0, 0, 90]
        ctl_orient.color = self.CTL_ORIENT_COLOR
        ctl_orient.shape_scale = self.SCALE * 3.5
        ctl_orient.shape_pos = [self.SCALE * 14, 0, 0]
        cmds.parent(ctl_orient.zro_grp_name, ctl_main.name)
        cmds.orientConstraint(ctl_orient.name, self.jnt_center)


        self.jnt_grp = cmds.group(n=self.JOINT_PREFIX + self._name + self.side_suffix + self.GROUP_SUFFIX, empty=1)
        cmds.parent(self.jnt_grp, ctl_main.name)
        self.lct_grp = cmds.group(n=self.LOCATOR_PREFIX + self._name + self.side_suffix + self.GROUP_SUFFIX, empty=1)
        cmds.setAttr(f"{self.lct_grp}.visibility", 0)
        dont_touch_list.append(self.lct_grp)

        # Same for eye lid up and eye lid down
        # Curve high, joints, controllers
        for STEP_INDEX, (vtx_list, suffix) in enumerate(zip(
                [self.vtx_eyelid_up, self.vtx_eyelid_dw],
                [self.UP_SUFFIX, self.DOWN_SUFFIX]
                )):

            vtx_pos = [cmds.xform(vtx, q=1, ws=1, t=1) for vtx in vtx_list]

            # Curve High
            crv_high = create_crv_with_pos_list(pos_list=vtx_pos, degree=1, name=self._name,
                                               prefix=self.CURVE_PREFIX, suffix=suffix + self.CURVE_HIGH_SUFFIX)
            self.crv_high.append(crv_high)

            lcts_aim = distribute_lct_on_crv(crv=crv_high, inst_number=len(vtx_list), constrained= True,
                                  param_u_start= 0.0, param_u_end= len(vtx_list)-1)

            # Joints
            jnts_start = []
            cmds.select(clear=1)
            for i, pos in enumerate(vtx_pos):
                # For corners of second curve, do not create jnts and lct
                is_first_vtx = i == 0
                is_last_vtx = i == len(vtx_pos)-1
                if STEP_INDEX == 1 and (is_first_vtx or is_last_vtx):
                    continue

                jnt_start = cmds.joint(n=f"{self.JOINT_PREFIX}start{suffix}{self.side_suffix}{i}", position=jnt_center_pos)

                jnt_end = cmds.joint(n=f"{self.JOINT_PREFIX}end{suffix}{self.side_suffix}{i}", position=pos, radius=0.5)
                cmds.select(clear=1)

                # Orient joints
                cmds.joint(jnt_start, e=1, oj="xyz", secondaryAxisOrient="yup", ch=False, zso=True)
                cmds.joint(jnt_end, e=1, oj="none", ch=False, zso=True)
                # cmds.parent(jnt_start, self.jnt_grp)

                lct = lcts_aim[i]
                cmds.xform(lct, ws=1, s=[0.2, 0.2, 0.2])

                cmds.aimConstraint(lct, jnt_start, mo=1, weight=1, aimVector=[1, 0, 0], upVector=[0, 1, 0],
                                   worldUpType="none")

                # aim_matrix_constraint(target=lct_aim, constrained=jnt_start, offset=False)
                jnts_start.append(jnt_start)
                self.bind_jnts.append(jnt_end)
            cmds.parent(*lcts_aim, self.lct_grp)
            cmds.parent(*jnts_start, self.jnt_grp)

            # Curve High
            crv_low = cmds.duplicate(crv_high)[0]
            crv_low = cmds.rename(crv_low, crv_high.replace(self.CURVE_HIGH_SUFFIX, self.CURVE_LOW_SUFFIX))
            crv_low = cmds.rebuildCurve(crv_low, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1,
                                        s=self.CTL_PER_EYE_LID - 1 , d=3, tol=0.01)[0]
            self.crv_low.append(crv_low)

            # get position of the curve points with the right indexes
            control_points_amount = self.CTL_PER_EYE_LID + 2
            control_points_indexes = [i for i in range(control_points_amount)]

            right_indexes = control_points_indexes.copy()
            right_indexes.pop(1)
            right_indexes.pop(-2)
            cvs_pos = [cmds.xform(f"{crv_low}.cv[{i}]", q=1, ws=1, t=1) for i in right_indexes]

            control_points_indexes[1] = (control_points_indexes[2], control_points_indexes[1])
            control_points_indexes.pop(2)
            control_points_indexes[-2] = (control_points_indexes[-3], control_points_indexes[-2])
            control_points_indexes.pop(-3)

            # Controllers with no duplicate at corners
            last_index = len(cvs_pos) - 1
            for i, pos in enumerate(cvs_pos):
                control_point_index = control_points_indexes[i]

                is_first_cv = i == 0
                is_last_cv = i == last_index
                if STEP_INDEX == 1 and (is_first_cv or is_last_cv): # do not repeat creating controller on corners
                    if is_first_cv:
                        ctl = self._ctls[0]
                    elif is_last_cv:
                        ctl = self._ctls[last_index]
                    dcm = cmds.createNode("decomposeMatrix", name="dcm_" + ctl.name)
                    cmds.connectAttr(f"{ctl.name}.worldMatrix[0]", f"{dcm}.inputMatrix")
                else:
                    ctl = Controller(name=f"{crv_low}{i}{self.side_suffix}")
                    ctl.pos = pos
                    ctl.shape = self.CTL_EYELID_SHAPE
                    ctl.shape_scale = self.SCALE
                    ctl.color = self.CTL_EYELID_COLOR
                    ctl.shape_rot = [90, 0, 0]
                    ctl.shape_pos = [0, 0, self.SCALE*2]

                    dcm = create_decompose_matrix_node(ctl.name)
                    cmds.connectAttr(f"{ctl.name}.worldMatrix[0]", f"{dcm}.inputMatrix")
                    self._ctls.append(ctl)
                if isinstance(control_point_index, tuple):
                    cmds.connectAttr(f"{dcm}.outputTranslate", f"{crv_low}Shape.controlPoints[{control_point_index[0]}]")
                    cmds.connectAttr(f"{dcm}.outputTranslate", f"{crv_low}Shape.controlPoints[{control_point_index[1]}]")
                else:
                    cmds.connectAttr(f"{dcm}.outputTranslate", f"{crv_low}Shape.controlPoints[{control_point_index}]")


            # Wire Deformer
            wire = cmds.wire(crv_high, name=self.WIRE_DEFORMER_PREFIX + crv_high, w=crv_low, gw=0, en=1.000000, ce=0.000000, li=0.000000)
            wire_name = crv_low + suffix + "BaseWire"
            cmds.rename(crv_low + "BaseWire", crv_low + suffix + "BaseWire")

            dont_touch_list.extend([crv_high, crv_low, wire_name])

        cmds.parent(*[ctl.zro_grp_name for ctl in self._ctls], self.ctl_main)

        # Attributes
        ctl = self.ctl_main
        add_separator_attribute(ctl.name, separator_name=self.BLINK_SUFFIX[1:])
        cmds.addAttr(ctl.name, ln=self.BLINK_SUFFIX + "_Height", at="float", keyable=1, max=1, min=0, dv=0.5)
        cmds.addAttr(ctl.name, ln=self.BLINK_SUFFIX, at="float", keyable=1, max=1, min=0, dv=0)

        # BS curve blink low mid
        crv_blink_mid = cmds.duplicate(crv_low, n=crv_low.replace(self.DOWN_SUFFIX+self.CURVE_LOW_SUFFIX, self.BLINK_SUFFIX))[0]

        bs_crv_blink = cmds.blendShape(self.crv_low[0], self.crv_low[1],  crv_blink_mid, name=self.BLEND_SHAPE_PREFIX + crv_blink_mid,
                                          origin="world", exclusive="characterPartition")[0]
        dont_touch_list.append(crv_blink_mid)

        # Attribute
        cmds.connectAttr(ctl.name + "." + self.BLINK_SUFFIX + "_Height", bs_crv_blink + "." + self.crv_low[0])
        reverse = cmds.createNode("reverse", n=ctl.name + "." + self.BLINK_SUFFIX + "_rev")
        cmds.connectAttr(ctl.name + "." + self.BLINK_SUFFIX + "_Height", f"{reverse}.inputX")
        cmds.connectAttr(f"{reverse}.outputX", f"{bs_crv_blink}.{self.crv_low[1]}")

        # duplicate crv_high for crv_high_blink
        # blend shape between crv_high_blink and crv_high
        # wire deformer between crv_blink_mid in up and down pose and crv_high_blink

        for crv_low, suffix, crv_high, weight in zip(self.crv_low, [self.UP_SUFFIX, self.DOWN_SUFFIX], self.crv_high, [1, 0]):
            # crv_high_blink
            crv_high_blink = cmds.duplicate(crv_high, n=crv_high + self.BLINK_SUFFIX)[0]

            # wire with bs at up or down pose
            # cmds.setAttr(f"{bs_crv_blink}.envelope", weight)
            cmds.setAttr(ctl.name + "." + self.BLINK_SUFFIX + "_Height", weight)
            wire = cmds.wire(crv_high_blink, w=crv_blink_mid, gw=0, en=1.000000, ce=0.000000, li=0.000000,dds=(0,self.SCALE*50))[0]
            cmds.setAttr(f"{wire}.scale[0]", 0)
            wire_name = crv_blink_mid + suffix + "BaseWire"
            cmds.rename(crv_blink_mid + "BaseWire", crv_blink_mid + suffix + "BaseWire")

            # BS crv_high
            bs_high = cmds.blendShape(crv_high_blink, crv_high, name=self.BLEND_SHAPE_PREFIX + crv_high,
                                                before=True, origin="world", exclusive="characterPartition",
                                                w=[(1, 1), (1, 1)])[0]

            # Attributes and max
            cmds.addAttr(ctl.name, ln=self.BLINK_SUFFIX + suffix, at="float", keyable=1, min=0, max=1, dv=0)
            max = cmds.createNode("max", n=crv_blink_mid + "_max")
            cmds.connectAttr(ctl.name + "." + self.BLINK_SUFFIX + suffix, f"{max}.input[0]")
            cmds.connectAttr(ctl.name + "." + self.BLINK_SUFFIX, f"{max}.input[1]")
            cmds.connectAttr(f"{max}.output", bs_high + "." + crv_high_blink, f=1)

            dont_touch_list.extend([crv_high_blink, wire_name])

        cmds.setAttr(ctl.name + "." + self.BLINK_SUFFIX + "_Height", 0.5)

        cmds.parent(*dont_touch_list, self.dont_touch_grp)


    def build_controller_constraints(self):
        up_ctls = self._ctls[:self.CTL_PER_EYE_LID]
        down_ctls = [self._ctls[0]] + self._ctls[self.CTL_PER_EYE_LID:] + [self._ctls[self.CTL_PER_EYE_LID-1]]

        # return
        half = self.CTL_PER_EYE_LID //2
        for ctl_list in [up_ctls, down_ctls]:
            # half lists ordered from the center controller
            first_half = ctl_list[:half+1][::-1]
            second_half = ctl_list[half:]

            for ctl_list in [first_half, second_half]:
                ctl_central = ctl_list[0]
                ctl_corner = ctl_list[-1]
                percent = 1/half
                for i, ctl in enumerate(ctl_list[1:-1]):

                    weight = logistic_interpolation(x=percent * (i + 1), L=1, k=5, x_zero=0.5)

                    cst = cmds.parentConstraint(ctl_central, ctl_corner, ctl.zro_grp_name, mo=True)[0]
                    # cmds.setAttr(f"{cst}.{ctl_central}W0", 1-percent * (i + 1))
                    cmds.setAttr(f"{cst}.{ctl_central}W0", 1 - weight)
                    # cmds.setAttr(f"{cst}.{ctl_corner}W1", percent * (i + 1))
                    cmds.setAttr(f"{cst}.{ctl_corner}W1", weight)
                # ctl_corner.shape = "round square"

        # ctl_central.shape = "round square"

    def build_fleshy_eyeLid(self):
        """
        Create an offset group onto corner and main ctls which translates x and y are connected to main jnt tuned rotates
        """
        half = self.CTL_PER_EYE_LID //2

        corner_ctls = [self._ctls[0], self._ctls[self.CTL_PER_EYE_LID-1]]

        center_ctls = [self._ctls[half], self._ctls[self.CTL_PER_EYE_LID + half - 1]]

        # mult rotate setup
        div = cmds.createNode("multiplyDivide", name="div_" + self.jnt_center)
        cmds.connectAttr(f"{self.jnt_center}.rotate", f"{div}.input1", f=1)
        cmds.setAttr(f"{div}.input2X", 0.07 * self.SCALE)
        cmds.setAttr(f"{div}.input2Y", 0.07 * self.SCALE)
        cmds.setAttr(f"{div}.input2Z", 0.07 * self.SCALE)
        for ctl in center_ctls:
            grp = ctl.add_offset_grp(suffix="_fleshy")
            cmds.connectAttr(f"{div}.outputY", f"{grp}.translateX", f=1)
            cmds.connectAttr(f"{div}.outputZ", f"{grp}.translateY", f=1)

        quarter = cmds.createNode("multiplyDivide", name="qrt_" + self.jnt_center)
        cmds.connectAttr(f"{div}.output", f"{quarter}.input1")
        cmds.setAttr(f"{quarter}.input2X", 0.4)
        cmds.setAttr(f"{quarter}.input2Y", 0.4)
        cmds.setAttr(f"{quarter}.input2Z", 0.4)
        for ctl in corner_ctls :
            grp = ctl.add_offset_grp(suffix="_fleshy")
            cmds.connectAttr(f"{quarter}.outputY", f"{grp}.translateX", f=1)
            cmds.connectAttr(f"{quarter}.outputZ", f"{grp}.translateY", f=1)

    # TO DO
    def build_fleshy_outer_eyeLid(self, vtx_eyelid_follow_up: list[str], vtx_eyelid_follow_bot: list[str]):
        pass
    # TO DO
    def build_eyeLid_stretch(self):
        pass


    # def set_input_and_output(self):
    #     self.input = self._ctl_chain[0]
    #     self.output = self._ctl_chain[-1]

    def arrange_nodes(self):
        obj_to_parent = [
            self.ctl_main.zro_grp_name,
        ]
        super().arrange_nodes(obj_to_parent)

    def bind_jnts(self, bind_jnts:list[str]=[]) -> list[str]:
        bind_jnts += [self.bind_jnts]
        return super().bind_jnts(bind_jnts=bind_jnts)
