from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.utils.api import rotate_ctl, lock_attributes, get_pole_vector_placement, create_annotation
from ..component.controller import Controller
from ..component.base import BaseComponent, ComponentType


class Limb(BaseComponent):
    """
    A Limb module contains :
        - a joint chain, must be well oriented at the beginning
        - a joint group
    Methods :
        - add offset controller and joint
    """

    TYPE = ComponentType.LIMB
    JOINT_PREFIX = "jnt_"
    CTL_OFFSET_COLOR = "red"
    CTL_OFFSET_SHAPE = "round square"

    def __init__(self, jnt_list:  list[str], name=None, duplicate_jnt=False, suffix="", scale=None):
        super().__init__(name)

        self._ctl_chain = []
        self.jnt_grp = None
        self._scale = scale
        self.has_offset_jnt = False
        self._offset_jnt_chain = []

        if not duplicate_jnt:
            self._jnt_chain = jnt_list
        else:
            self._jnt_chain = self._duplicate_jnt_chain(jnt_list, suffix=suffix)

    def _duplicate_jnt_chain(self, jnt_list: list[str], suffix: str =""):
        """
        Create a duplicate of the joint chain with new suffix
        """
        self.jnt_grp = cmds.group(empty=True, name=jnt_list[0] + suffix + self.GROUP_SUFFIX)

        jnt_created = []

        for jnt in jnt_list:

            if self.JOINT_PREFIX in jnt:
                new_jnt_name = jnt + suffix
            elif "_" in jnt:
                new_jnt_name = self.JOINT_PREFIX + jnt.split('_')[1] + suffix
            else:
                new_jnt_name = self.JOINT_PREFIX + jnt + suffix

            cmds.select(clear=1)
            new_jnt = cmds.joint(n=new_jnt_name)

            cmds.matchTransform(new_jnt, jnt)
            cmds.makeIdentity(new_jnt, apply=1, t=1, r=1, s=1)

            # for axis in ["X", "Y", "Z"]:
            #     cmds.setAttr(f'{new_jnt}.jointOrient{axis}', 0)

            jnt_created.append(new_jnt)

        cmds.parent(jnt_created[0], self.jnt_grp)

        for i in range(len(jnt_created)):
            if i > 0:
                cmds.parent(jnt_created[i], jnt_created[i-1])

        return jnt_created

    def build_offset_controller(self):
        self._offset_jnt_chain = []

        for jnt in self.jnts:
            cmds.select(clear=1)
            ctl = Controller(jnt + "offset")
            ctl.color = self.CTL_OFFSET_COLOR
            ctl.shape = self.CTL_OFFSET_SHAPE
            ctl.shape_scale = 0.7
            ctl.shape_rot = (0, 0, 90)

            offset_jnt = cmds.joint(name=jnt + "offset")
            self._offset_jnt_chain.append(offset_jnt)

            # cmds.parent(offset_jnt, ctl)
            cmds.matchTransform(ctl.name, jnt)
            cmds.parent(ctl.zro_grp_name, jnt)



        self.has_offset_jnt = True


    @property
    def jnts(self):
        if self.has_offset_jnt:
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

    @property
    def scale(self):
        if not self._scale:
            cmds.xform(self.jnts[1], q=1, ws=1, m=1)
        else:
            return self._scale


class FkLimb(Limb):
    """
    A FkLimb module contains :
        - a joint chain
        - a ctl group
        - a FK ctl chain
    """

    TYPE = ComponentType.FK_LIMB
    FK_PREFIX = "_FK"
    CTL_COLOR = "green"
    CTL_SHAPE = "circle"

    def __init__(self, jnt_list:  list[str]):

        if jnt_list == []:
            self._ctl_chain = []
            self.ctl_grp_name = None
            cmds.error("Empty FK limb")
            return

        # duplicate the joint chain with '_FK' suffix and store it
        super().__init__(jnt_list, duplicate_jnt=True, suffix=self.FK_PREFIX)

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
            ctl.shape = self.CTL_SHAPE
            ctl.color = self.CTL_COLOR
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
        (- bendy)
        (- stretchy)
    """

    TYPE = ComponentType.IK_LIMB
    IK_PREFIX = "_IK"
    CTL_COLOR = "red"
    CTL_SHAPE = "box"
    CTL_POLE_SHAPE = "sphere"


    def __init__(self, jnt_list: list[str], pole_vector=False):

        if jnt_list == []:
            self._ctl_chain = []
            self.ctl_grp_name = None
            self.ik_handle = None
            cmds.error("Empty IK limb")
            return

        # duplicate the joint chain with '_IK' suffix and store it
        super().__init__(jnt_list, duplicate_jnt=True, suffix=self.IK_PREFIX)

        if cmds.objExists(Controller.CONTROLLER_PREFIX + jnt_list[-1] + self.IK_PREFIX):
            self.build_from_scene_data(self.jnts)
        else:
            self.build(self.jnts)

        if pole_vector:
            self.build_pole_vector()

    # -- Builder

    def build(self, jnt_list: list[str]):
        """
        Build the IK limb by creating Ik ctl on the last jnt and store it in self._ctl_chain
        """

        ctl = Controller(self.jnts[-1])
        ctl.shape = self.CTL_SHAPE
        ctl.color = self.CTL_COLOR
        ctl.pos = cmds.xform(self.jnts[-1], q=1, ws=1, t=1)
        ctl.rot = cmds.xform(self.jnts[-1], q=1, ws=1, ro=1)

        cmds.connectAttr(f"{ctl}.rotate", f"{self.jnts[-1]}.rotate")

        self._ctl_chain = [ctl]

        self.ik_handle = cmds.ikHandle(name=self.ctl.name + "_IKHandle",
                                  startJoint=self.jnts[0],
                                  endEffector=self.jnts[-1],
                                  solver='ikRPsolver')[0]

        cmds.parent(self.ik_handle, self.ctl)

        self.ctl_grp_name = cmds.group(self._ctl_chain[0].zro_grp_name, name=self._ctl_chain[0].name + self.GROUP_SUFFIX)

    def build_from_scene_data(self, jnt_list: list[str]):
        pass

    def build_pole_vector(self):
        if not len(self.jnts) == 3:
            return

        lct = get_pole_vector_placement(*self.jnts)
        new_lct_name = f"lct_{self.ctl}_pole_vector"
        cmds.rename(lct, new_lct_name)
        lct = new_lct_name

        cmds.poleVectorConstraint(lct, self.ik_handle, w=1)
        cmds.setAttr(f'{lct}Shape.visibility', 0)

        create_annotation(self.jnts[1], lct)

        ctl = Controller(self.ctls[0].name + "_pole_vector")
        ctl.shape = self.CTL_POLE_SHAPE
        ctl.color = self.CTL_COLOR
        ctl.pos = cmds.xform(lct, q=1, ws=1, t=1)
        ctl.rot = cmds.xform(lct, q=1, ws=1, ro=1)

        cmds.parent(ctl.zro_grp_name, self.ctl_grp_name)
        cmds.parent(lct, ctl)


class IkFkLimb(Limb):

    MODULE_TYPE = ComponentType.IK_FK_LIMB
    IK_FK_SUFFIX = "_blend"
    SWITCH_SUFFIX = "_switch_IK_FK"
    CTL_COLOR = "blue"
    CTL_SHAPE = "double arrow"

    def __init__(self, jnt_list: list[str], name=None):
        Limb.__init__(self, jnt_list=jnt_list, name=name, duplicate_jnt=True, suffix=self.IK_FK_SUFFIX)

        self.fk_limb = FkLimb(jnt_list)
        self.ik_limb = IkLimb(jnt_list, pole_vector=True)

        self._build_ik_fk(jnt_list)


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

    def build_stretch(self):
        pass

    def build_bendy(self):
        pass




