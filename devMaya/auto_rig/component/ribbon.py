from maya import cmds

from devMaya.auto_rig.component.base import BaseComponent, ComponentType
from devMaya.auto_rig.component.composed import ComposedComponent
from devMaya.auto_rig.configs.config import Config
from devMaya.utils.position import lerp_pos
from devMaya.utils.nurbs_curve import create_crv_with_obj_list
from devMaya.utils.follicle import create_flc_on_surface
from devMaya.utils.controller import create_ctl, create_ctls
from devMaya.utils.joint import create_jnt, create_jnts, reset_jnts_orient

class Ribbon(ComposedComponent):
    """
    A Ribbon component contains :
        - A surface : srf_name
        - Follicles and a follicle grp
        - A side suffix : _L, _R, or None
        ...
    """

    COMPONENT_TYPE = ComponentType.RIBBON

    SURFACE_PREFIX = "srf_"
    FOLLICLE_PREFIX = "flc_"
    SUFFIX = ""

    CTL_OFFSET_SHAPE = "root"
    CTL_OFFSET_COLOR = "yellow"

    ADD_SINE_DEFORMER = False
    CONSTRUCTION_HISTORY = False

    def __init__(self, name: str = None, config: Config = None):
        super().__init__(name=name, config=config)

        self._flcs = []
        self.flc_grp_name = None
        self._ctls = []
        self._jnts = []

    def distribute_follicles(self,
            flc_on_u=1,
            flc_on_v=1,

            flc_param_u_start=0,
            flc_param_u_end=1,
            flc_param_u_offset=0,

            flc_param_v_start=0,
            flc_param_v_end=1,
            flc_param_v_offset=0
            ):
        """
        Add custom amount of follicles to ribbon
        """

        self._flcs = create_flc_on_surface(
            surface=self.name,
            flc_on_u=flc_on_u,
            flc_on_v=flc_on_v,

            flc_param_u_start=flc_param_u_start,
            flc_param_u_end=flc_param_u_end,
            flc_param_u_offset=flc_param_u_offset,

            flc_param_v_start=flc_param_v_start,
            flc_param_v_end=flc_param_v_end,
            flc_param_v_offset=flc_param_v_offset,
            suffix = self.FOLLICLE_PREFIX
        )

        self.flc_grp_name = cmds.group(name=self.FOLLICLE_PREFIX + self.name + self.GROUP_SUFFIX, empty=1)

        cmds.parent(*self._flcs, self.flc_grp_name)


    def add_offset_ctls(self):
        """
        Add offset controllers inside follicles
        """
        for flc in self._flcs:
            ctl = create_ctl(flc, zro_grp=True, parent=1)
            ctl.shape = self.CTL_OFFSET_SHAPE
            ctl.color = self.CTL_OFFSET_COLOR
            ctl.shape_scale = self.SCALE * 0.5
            ctl.shape_rot = [0, 0, 90]
            self._ctls.append(ctl)

        if self._jnts:
            try:
                [cmds.parent(jnt, ctl) for jnt, ctl in zip(self._jnts, self._ctls)]
            except:
                pass

    def add_jnts(self):
        """
        Add jnts inside follicles or inside offset controllers if self.ADD_JOINTS = True
        """
        for flc in self._flcs:
            jnt = create_jnt(flc, parent=1, radius=0.5)
            self._jnts.append(jnt)

        if self._ctls:
            try:
                [cmds.parent(jnt, ctl) for jnt, ctl in zip(self._jnts, self._ctls)]
            except:
                pass

        reset_jnts_orient(self._jnts)

    @BaseComponent.name.getter
    def name(self):
        return self.SURFACE_PREFIX + BaseComponent.name.fget(self)

    @property
    def jnts(self):
        return self._jnts

    @property
    def ctls(self):
        return self._ctls

    @property
    def flcs(self):
        return self._flcs

    # @BaseComponent.side_suffix.setter
    # def side_suffix(self, side):
    #     side = self.side_suffix
    #     BaseComponent.side_suffix.fset(self, side)
    #     print("in ribbon actual, new", side, self.side_suffix)


class LimbRibbon(Ribbon):
    """
    A Special Ribbon component built along a chain of joints for bendy limbs
    """

    def __init__(self, jnt_list: list[str], name: str = None, config: Config = None):
        super().__init__(name=name, config=config)

        self._jnt_list = jnt_list

        self._build()

    def __build_wit_extrusion(self):
        """
        Not used, not working
        Create two curves and extrude them to obtain a surface
        """
        crv_1 = create_crv_with_obj_list(self._jnt_list, name="crv_1", crv_subdivision=2, degree=3)
        # cvs_pos_1 = [cmds.xform(jnt, q=1, ws=1, t=1) for jnt in self._jnt_list]
        # cvs_pos_1.insert(1, lerp_pos(cvs_pos_1[0], cvs_pos_1[1], .2))
        # cvs_pos_1.insert(-1, lerp_pos(cvs_pos_1[-2], cvs_pos_1[-1], .8))
        # crv_1 = cmds.curve(name = self.CURVE_PREFIX + self._name + "_1", p=cvs_pos_1, d=1)

        cvs_pos_2 = [[0, 0, 0], [0.2 * self.SCALE, 0, 0], [0.8 * self.SCALE, 0, 0], [1 * self.SCALE, 0, 0]]
        crv_2 = cmds.curve(name = self.CURVE_PREFIX + self._name + "_2", p=cvs_pos_2, d=3)
        cmds.xform(crv_2, ws=1, t=[-self.SCALE * 0.5, 0, 0], )
        cmds.CenterPivot(crv_2)
        cmds.xform(crv_2, ws=1, ro = [0, 90, 0])
        cmds.makeIdentity(crv_2, apply=True, r=1, t=1)

        self.crv_list.extend([crv_1, crv_2])

        cmds.matchTransform(crv_2, self._jnt_list[0], rotation=True, scale=False, position=True)

        srf = cmds.extrude(crv_1, crv_2, name=self.name,
                           ch=self.CONSTRUCTION_HISTORY,
                           rn=False,
                           po=0,
                           et=2, # choose component pivot to extrude
                           ucp=1,
                           fpt=False, # lock extrusion along second crv path
                           upn=True,
                           rotation=0, scale=1,
                           rsp=1,
                           )
        srf = cmds.extendSurface(srf, ch=self.CONSTRUCTION_HISTORY, extendSide=0, extensionType = 0, extendDirection=1)

    def _build(self):
        """
        Build the ribbon component with a curve and two offset curves lofted
        """
        crv_base = create_crv_with_obj_list(self._jnt_list, name="crv_base", crv_subdivision=1, degree=3)

        crv_1 = cmds.offsetCurve(crv_base, ch=self.CONSTRUCTION_HISTORY, d=self.SCALE/2, rn=False, cb=2, st=True, cl=True, cr=0, tol=0, sd=0, ugn=False)
        crv_2 = cmds.offsetCurve(crv_base, ch=self.CONSTRUCTION_HISTORY, d=-self.SCALE/2, rn=False, cb=2, st=True, cl=True, cr=0, tol=0, sd=0, ugn=False)

        srf = cmds.loft(crv_1, crv_2, name=self.name, ch=self.CONSTRUCTION_HISTORY, u=1, c=0,
                             ar=1, d=1, ss=1, rn=0, po=0, rsn=True)

        if not self.CONSTRUCTION_HISTORY:
            cmds.delete(crv_base, crv_1, crv_2)


class TwoCurvesRibbon(Ribbon):
    """
    A Special Ribbon component built with two custom curves lofted
    """

    def __init__(self, crv_list: list[str], name: str = None, config: Config = None):
        super().__init__(name=name, config=config)

        self._crv_list = crv_list

        self.build()

    def build(self):
        srf = cmds.loft(*self._crv_list, name=self.name, ch=self.CONSTRUCTION_HISTORY, u=1, c=0,
                             ar=1, d=3, ss=1, rn=0, po=0, rsn=True)

        if not self.CONSTRUCTION_HISTORY:
            cmds.delete(*self._crv_list)
