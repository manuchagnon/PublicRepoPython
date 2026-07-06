from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from ..component.composed import ComposedComponent
from devMaya.auto_rig.modules.ik_fk import IkFk
from devMaya.auto_rig.modules.foot import Foot
from devMaya.auto_rig.configs.config import Config
from ..component.controller import Controller

class Leg(IkFk):
    """
    A leg can receive foot at init

    """
    TYPE = ModuleType.LEG

    BUILD_ROOT_CTL: bool = True
    BUILD_BENDY: bool = True
    BUILD_OFFSET_CTL: bool = True
    BUILD_STRETCHY: bool = True

    IK_FK_SWITCH: int | bool = 1

    CTL_POLE_PARENTS_NAME: list[str] = ["normal", "thigh"]

    def __init__(self, jnt_list: list[str], name=None, foot: Foot | None = None, config: Config = None):
        super().__init__(jnt_list=jnt_list, name=name, config=config)

        pos = cmds.xform(self.ik_fk_limb.jnts[0], q=1, ws=1, t=1)
        self.ik_fk_limb.ctl_param.pos = [pos[0] + -2 * self.SCALE, pos[1], pos[2]]

        # if isinstance(foot, Foot):
        #     self._foot = foot
        # else:
        #     self._foot = None

    def build_switch_parent_setup_on_ctl(self,
                                         parents_modules: list[BaseModule],
                                         switch_parent_ctl=None,
                                         parents_controllers=[],
                                         parent_at_start: Controller | BaseModule = None,
                                         ctl_ik_override_names=[],
                                         ctl_pole_override_names=[]
                                         ):

        if not ctl_ik_override_names:
            ctl_ik_override_names = self.CTL_IK_PARENTS_NAME
        if not ctl_pole_override_names:
            ctl_pole_override_names = self.CTL_POLE_PARENTS_NAME

        super().build_switch_parent_setup_on_ctl(parents_modules=parents_modules,
                                                 switch_parent_ctl=switch_parent_ctl,
                                                 parents_controllers=parents_controllers,
                                                 parent_at_start=parent_at_start,
                                                 ctl_ik_override_names=ctl_ik_override_names,
                                                 ctl_pole_override_names=ctl_pole_override_names)

    # @property
    # def foot(self):
    #     return self._foot
    #
    # @foot.setter
    # def foot(self, foot):
    #     # if not isinstance(foot, Feet):
    #     #     print("Cannot set foot because", foot, "is not an instance of Feet :", type(foot))
    #     #     return
    #     self._foot = foot


    # testing
    # def duplicate(self) -> ComposedComponent | None:
    #     print("leg ", self.name,"want duplicate, so it duplicates its foot first", self.get_actual_component(self._foot))
    #     if self._foot:
    #         self._foot = self.get_actual_component(self._foot).duplicate()
    #     res = super().duplicate()
    #     print("TETETETE", res, res.name, res.side_suffix)
    #     return res
    #
    # def mirror(self, axis=[-1, 1, 1]):
    #     print("leg ", self.name,"want mirror, so it mirrors its foot first", self.get_actual_component(self._foot))
    #     if self._foot:
    #         self.get_actual_component(self._foot).mirror(axis=axis)
    #     super().mirror()

