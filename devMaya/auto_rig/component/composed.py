from maya import cmds

from enum import Enum, auto

from devMaya.auto_rig.component.base import BaseComponent
from devMaya.auto_rig.component.controller import ControllerShapes, Controller
from devUi.utils.colors import Colors
from devMaya.auto_rig.configs.config import Config
from devMaya.utils.api import (
    lock_attributes,
)



class ComposedComponent(BaseComponent):
    """
    A ComposedComponent is used when a component could be made of several BaseComponents
    So it represents a majority of components and all modules

    It adds attributes like ctl_param

    """

    CTL_PARAMETER_SUFFIX : str = "_param"
    CTL_PARAMETER_COLOR : Colors | str = "blue"
    CTL_PARAMETER_SHAPE : ControllerShapes | str = "double arrow"

    def __init__(self, name: str = None, config: Config = None):
        super().__init__(name=name, config=config)

        self.ctl_param = None

    def build_ctl_param(self, name : str) -> Controller:
        """
        Create a controller parameter to hold attributes like switch If Fk or wind
        """
        ctl = Controller(name + self.CTL_PARAMETER_SUFFIX)

        ctl.shape = self.CTL_PARAMETER_SHAPE
        ctl.shape_scale = self.SCALE * 0.4
        ctl.color = self.CTL_PARAMETER_COLOR

        lock_attributes(ctl.name, attr_name="all")

        self.ctl_param = ctl

        return ctl