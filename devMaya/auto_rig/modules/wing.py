from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.modules.ik_fk import IkFk
from devMaya.auto_rig.component.base import BaseComponent, ComponentType
from devMaya.auto_rig.component.limb import IkFkLimb, IkLimb, FkLimb
from devMaya.auto_rig.component.ribbon import Ribbon, TwoCurvesRibbon
from devMaya.auto_rig.component.controller import ControllerShapes, Controller
from devUi.utils.colors import Colors
from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.decorators import use, UseType


from devMaya.utils.api import (
    find_closest_vertex_to_point,
    find_furthest_vertex_to_point,
    subdivide_jnt_chain,
    get_pos_with_parameter_u,
    connect_attributes,
    lock_attributes,
    create_jnt_chain,
    add_separator_attribute,
    create_set,
)
from devUtils.maths import remap_value


class Feather(FkLimb):

    TYPE : ComponentType = ComponentType.FEATHER

    def __init__(self, jnt_list:list[str], name=None, feather_subdivision=2, config: Config=None):

        jnt_chain = subdivide_jnt_chain(jnt_list, in_between_jnt=feather_subdivision)

        super().__init__(jnt_chain, duplicate_jnt=False, config=config)
        root_ctl = self.build_root_ctl()
        root_ctl.shape_scale = 2

        # Hide the last Controller because joint has to stay at the same place when mirrored
        cmds.setAttr(f"{self.ctls[-1].shape}.visibility", 0)

        self._start_pos = cmds.xform(jnt_chain[0], q=1, ws=1, t=1)
        self._end_pos = cmds.xform(jnt_chain[-1], q=1, ws=1, t=1)

        self._name = name

    @property
    def start_pos(self):
        return self._start_pos

    @property
    def end_pos(self):
        return self._end_pos


class Wing(IkFk):
    """
    A Wing module contains :
        - an IkFkLimb component
        - input and output locators

        - several feathers mesh
        - several FKLimb components for the feathers
    """

    TYPE : ModuleType = ModuleType.WING

    BUILD_ROOT_CTL : bool = True
    BUILD_BENDY : bool = True
    BUILD_OFFSET_CTL : bool  = True

    CTL_PARAMETER_SUFFIX : str = "_parameter"
    CTL_PARAMETER_COLOR : Colors | str = "blue"
    CTL_PARAMETER_SHAPE : ControllerShapes | str = "star pointy"

    POLE_VECTOR_DISTANCE : float = 20.0

    FEATHER_SUBDIVISION : int = 2
    CTL_FEATHER_SCALE : float = 0.5
    CTL_FEATHER_COLOR : Colors | str = "orange"

    def __init__(self, jnt_list: list[str], name=None, config: Config=None):
        new_config = Config({"POLE_VECTOR_DISTANCE" : self.POLE_VECTOR_DISTANCE})
        if config:
            new_config += config

        super().__init__(jnt_list, name=name, config=new_config)

        self._main_locator = None
        self._feather_meshes = []
        self._feathers = []

        self.main_jnt_chains: list[list[str]] = []
        self.ribbon = None

        self._build_wing()
        # self.set_input_and_output()
        # self.arrange_nodes()

    def _build_wing(self):
        """
        Create parameter controller for special attributes added in further methods
        """
        ctl = self.build_ctl_param(name=self.name)
        # pos = cmds.xform(self.jnts[0], q=1, ws=1, t=1)
        # ctl.pos = [pos[0], pos[1] + 2 * self.SCALE, pos[2]]
        ctl.shape_rot = [90, 0 ,0]
        cmds.parent(ctl.zro_grp_name, self.ik_fk_limb.jnts[-1])
        cmds.xform(ctl.zro_grp_name, os=1, ro=[0, 0, 0], t=[0, 0, 0])
        cmds.move(self.SCALE * 3, self.SCALE * -3, 0, ctl.zro_grp_name, os=1)

        lock_attributes(ctl, attr_name="all")

        cmds.parent(ctl.zro_grp_name, self.ik_fk_limb.ctl_root)

        # ctl = Controller(name=self.name + self.CTL_PARAMETER_SUFFIX)
        # ctl.shape = self.CTL_PARAMETER_SHAPE
        # ctl.shape_rot = [90, 0 ,0]
        # ctl.shape_scale = self.SCALE * 0.5
        # ctl.color = self.CTL_PARAMETER_COLOR
        # cmds.parent(ctl.zro_grp_name, self.ik_fk_limb.jnts[-1])
        # cmds.xform(ctl.zro_grp_name, os=1, ro=[0, 0, 0], t=[0, 0, 0])
        # cmds.move(self.SCALE * 3, self.SCALE * -3, 0, ctl.zro_grp_name, os=1)
        #
        # lock_attributes(ctl, attr_name="all")
        #
        # cmds.parent(ctl.zro_grp_name, self.ik_fk_limb.ctl_root)
        #
        #
        # self.ctl_param = ctl

    def _create_main_jnt_chain(self, index:int, jnt_chain=None):
        if not jnt_chain:
            ctl_start = self.ik_fk_limb.offset_ctl_chain[index]
            jnt_start = self.main_jnt_chains[-1][0]
            jnt_start_2 = self.main_jnt_chains[0][0]
            jnt_end = self.main_jnt_chains[-1][1]
            main_jnt_chain = create_jnt_chain([ctl_start, jnt_end], suffix="_main")
            cmds.orientConstraint(jnt_start_2, jnt_start, main_jnt_chain[0], mo=False)
            self.main_jnt_chains.insert(1, main_jnt_chain)
        else:
            ctl_start = self.ik_fk_limb.offset_ctl_chain[index]
            jnt_start = jnt_chain[0]
            jnt_end = jnt_chain[1]
            main_jnt_chain = create_jnt_chain([ctl_start, jnt_end], suffix="_main")
            cmds.matchTransform(main_jnt_chain[0], jnt_start, rot=True)
            self.main_jnt_chains.append(main_jnt_chain)
        cmds.parent(main_jnt_chain[0], ctl_start)

    # Build Feathers
    @use(UseType.UNIQUE | UseType.EXCLUDING)
    def build_feathers_rig_with_meshes(self, feathers_meshes_list:list[str], main_locator:str):
        if not (feathers_meshes_list and main_locator):
            return None

        self._feather_meshes = feathers_meshes_list

        center_pos = cmds.xform(main_locator, ws=1, q=1, t=1)

        for feather_mesh in self._feather_meshes:
            closest_index, closest_pos = find_closest_vertex_to_point(feather_mesh, center_pos)
            self._start_pos = closest_pos

            furthest_index, furthest_pos = find_furthest_vertex_to_point(feather_mesh, center_pos)
            self._end_pos = furthest_pos

            cmds.select(clear=1)
            jnt_start = cmds.joint(name=f"jnt_{feather_mesh}_start")
            pos = cmds.xform(f"{feather_mesh}.vtx[{closest_index}]", q=1, ws=1, t=1)
            cmds.xform(jnt_start, ws=1, t=pos)

            jnt_end = cmds.joint(name=f"jnt_{feather_mesh}_end")
            pos = cmds.xform(f'{feather_mesh}.vtx[{furthest_index}]', q=1, ws=1, t=1)
            cmds.xform(jnt_end, ws=1, t=pos)

            cmds.joint(jnt_start, e=1, oj=self.JNT_ORIENT, secondaryAxisOrient="yup", ch=1, zso=1)
            cmds.joint(jnt_end, e=1, oj="none", ch=1, zso=1)

            jnt_chain = [jnt_start, jnt_end]

            if feather_mesh == self._feather_meshes[0] :
                self._create_main_jnt_chain(0, jnt_chain=jnt_chain)
            elif feather_mesh == self._feather_meshes[-1]:
                self._create_main_jnt_chain(-1, jnt_chain=jnt_chain)
                self._create_main_jnt_chain(int(len(self.ik_fk_limb.offset_ctl_chain) / 2), jnt_chain=None)

            feather_config = Config({
                "SCALE": self.SCALE * self.CTL_FEATHER_SCALE,
                "CTL_FK_COLOR": self.CTL_FEATHER_COLOR,
            })

            feather = Feather(jnt_chain, name = self.name, feather_subdivision=self.FEATHER_SUBDIVISION, config=feather_config)
            # feather.build_feather_with_mesh(feather_mesh, feather_subdivision=self.FEATHER_SUBDIVISION, center_pos=center_pos)
            cmds.parent(feather.ctl_grp_name, self.ik_fk_limb.ctl_root)

            self._feathers.append(feather)

        return None

    @use(UseType.UNIQUE | UseType.EXCLUDING)
    def build_feathers_rig_with_joint_chains(self, jnt_chains:list[list[str]]):
        if not jnt_chains and not all([isinstance(jnt_chain) == list[str] for jnt_chain in jnt_chains]):
            return None

        # build main feather controls

        self._create_main_jnt_chain(0, jnt_chain=jnt_chains[0])
        self._create_main_jnt_chain(-1, jnt_chain=jnt_chains[-1])
        self._create_main_jnt_chain(int(len(self.ik_fk_limb.offset_ctl_chain) / 2), jnt_chain=None)

        for jnt_chain in jnt_chains:
            feather = Feather(jnt_chain, name = self.name, feather_subdivision=self.FEATHER_SUBDIVISION, config=self.FEATHER_CONFIG)
            cmds.parent(feather.ctl_grp_name, self.ik_fk_limb.ctl_root)

            self._feathers.append(feather)

    @use(UseType.UNIQUE | UseType.UNNECESSARY)
    def build_feathers_aim_setup(self):
        """
        Create curves and aim constraints
        """
        if not self._feathers:
            print("Build Feathers first \nWith meshes or jnt_chains")
            return
        crv_out_pos_list = [feather.end_pos for feather in self._feathers]
        crv_out = cmds.curve(p=crv_out_pos_list, name=self.CURVE_PREFIX + "_out_feathers", degree=1)

        crv_in_pos_list = [feather.start_pos for feather in self._feathers]
        crv_in = cmds.curve(p=crv_in_pos_list, name=self.CURVE_PREFIX + "_in_feathers", degree=1)

        # curve to bind to middle offset ctl
        # smooth_crv_out = cmds.rebuildCurve(crv_out, name=self.CURVE_PREFIX +"_offset_smooth_feathers",
        #                                    ch=False, rpo=0, rt=0,
        #                                    end=1, kr=1, kcp=0, kep=1,
        #                                    s=5, d=self.SCALE * 2, tol=0.01)[0]

        # curve offset for aim constraints
        crv_offset = cmds.offsetCurve(crv_out, name=self.CURVE_PREFIX +"_offset_feathers",
                                      d=-self.SCALE * 3, ch=False, rn=False, cb=1, st=True, cl=True, cr=0,
                                      tol=1, sd=5, ugn=False)[0]



        length = len(self._feathers)

        # Ribbon surface for follicles
        self.ribbon = TwoCurvesRibbon(crv_list=[crv_out, crv_in], name=self.name)
        # Skin the ribbon
        cmds.skinCluster(
            *self.main_jnt_chains,
            self.ribbon.name,
            n=f'{self.ribbon.name}_skinCluster',
            maximumInfluences=4,
            dropoffRate=0.5,
            obeyMaxInfluences=1
        )
        self.ribbon.distribute_follicles(flc_on_u=length, flc_on_v=2)
        cmds.parent(self.ribbon.name, self.dont_touch_grp)
        cmds.parent(self.ribbon.flc_grp_name, self.dont_touch_grp)

        # Aim setup with aim controller
        for i in range(length):
            pos = get_pos_with_parameter_u(crv_offset, float(i))
            ctl = Controller(name=str(i))
            ctl.pos = pos
            ctl.color = "red"
            ctl.shape = "arrow"
            ctl.shape_scale = 0.5
            ctl.shape_rot = [0, -90, 0]
            cmds.parent(ctl.zro_grp_name, self.ribbon.flcs[i * 2])
            cmds.xform(ctl.zro_grp_name, os=True, ro=[90, 0, -90])

            feather = self._feathers[i]
            # this setup has to be a FkLimb method because i need it in other module !!
            grp = feather.ctls[0].add_offset_grp(suffix="AIM")
            ctl_root = feather.ctl_root
            lct_constrained = cmds.spaceLocator(name="lct_" + ctl_root.name + "AIM")[0]
            cmds.matchTransform(lct_constrained, ctl_root.zro_grp_name)
            cmds.parent(lct_constrained, ctl_root.zro_grp_name)
            lct_target = cmds.spaceLocator(name="lct_" + ctl.name + "AIM")[0]
            cmds.setAttr(f"{lct_target}.visibility", 0)
            cmds.matchTransform(lct_target, self.ribbon.flcs[i * 2])
            cmds.parent(lct_target, ctl)
            cmds.aimConstraint(lct_target, lct_constrained, mo=1) # do not work with other side
            # cmds.orientConstraint(lct, grp, mo=0)
            connect_attributes(lct_constrained, grp, attributes_list=["rotate"])

            feather.build_quick_rotation_setup(ctl_target_rotation=ctl)

            cmds.parent(feather.ctl_root.zro_grp_name, self.ribbon.flcs[i*2 +1])
        cmds.delete(crv_offset)

    @use(UseType.UNIQUE | UseType.UNNECESSARY)
    def build_wind_setup(self, feathers_orientation = "horizontal"):
        if not self.ribbon:
            print("Build Aim first")
            return

        add_separator_attribute(obj=self.ctl_param, separator_name="Wind")

        cmds.addAttr(self.ctl_param.name, ln="Wind_Weight", at="float", keyable=1, max=1, min=0, dv=0)
        cmds.addAttr(self.ctl_param.name, ln="Wind_Amplitude", at="float", keyable=1, min=0, max=10, dv=0)
        cmds.addAttr(self.ctl_param.name, ln="Wind_Offset", at="float", keyable=1, min=0, dv=0)

        length = len(self._feathers)

        # Wind Setup
        def create_sine_deformer(srf:str, suffix:str, wave_length:float, rotation:list[float]):
            sine_deformer, sine_handle = cmds.nonLinear(srf, name=srf + suffix + "_sine", type='sine', amplitude=0.05,
                                        wavelength=wave_length, frontOfChain=True, lowBound=-10, highBound=10)
            cmds.xform(sine_deformer + "Handle", ws=True, ro=rotation)
            if feathers_orientation == "vertical": # orient sine deformer if feathers are vertical
                cmds.rotate(90, 0, 0, sine_deformer + "Handle", r=1, ws=1, fo=1)
            else:
                pass
            cv_to_prune = f"{self.ribbon}.cv[0:{length - 1}][3]"
            cmds.percent(sine_deformer, cv_to_prune, value=0.0)
            for i in range(length//2):
                def weight_function(x):
                    return 0.3 * (x ** 2) + 0.2 * x + 0.2
                weight = weight_function(i)
                new_weight = remap_value(weight, old_start=0.2, old_end=weight_function(length//2), new_start=0.0, new_end=1.0)
                cv_to_prune = f"{self.ribbon}.cv[{i}][0:2]"
                cmds.percent(sine_deformer, cv_to_prune, value=new_weight)
                # cv_to_prune = f"{self.ribbon}.cv[1][0:2]"
                # cmds.percent(sine_deformer, cv_to_prune, value=0.5)
            cmds.connectAttr(self.ctl_param.name + ".Wind_Weight", f"{sine_deformer}.envelope", f=1)
            cmds.connectAttr(self.ctl_param.name + ".Wind_Amplitude", f"{sine_deformer}.amplitude", f=1)
            cmds.connectAttr(self.ctl_param.name + ".Wind_Offset", f"{sine_deformer}.offset", f=1)
            cmds.setAttr(f"{sine_handle}.visibility", 0)
            cmds.parent(sine_handle, self.dont_touch_grp)
            return sine_deformer

        sine_small = create_sine_deformer(srf=self.ribbon.name, suffix= "_small", wave_length=0.08, rotation=[180, 0, 90])
        sine_big = create_sine_deformer(srf=self.ribbon.name, suffix="_big", wave_length=0.25, rotation=[45,0,-70])

    @property
    def feathers(self):
        return self._feathers

    def arrange_nodes(self, obj_to_parent=[]):
        obj_to_parent += [
            *[self._feathers[i].jnts[0] for i in range(len(self._feathers))],
        ]
        super().arrange_nodes(obj_to_parent)
        return

    def set_input_and_output(self, input : str =None, output : str = None, input_pos=None, output_pos=None):
        """
        TO DO
        """
        pass

    def bind_jnts(self, bind_jnts:list[str]=[]) -> list[str]:
        bind_jnts += [jnt for jnt in [feather.jnts for feather in self._feathers]]
        return super().bind_jnts(bind_jnts=bind_jnts)