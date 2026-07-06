from maya import cmds

import copy
from enum import Enum, auto
from abc import ABC, abstractmethod

from ..component.base import BaseComponent
from ..component.composed import ComposedComponent
from ..component.controller import Controller
from devMaya.utils.api import (
    get_hierarchy_list_from_root_node,
    replace_in_names,
    create_set,
    Attribute, Separator,
    create_switch_parent_setup_on_ctl,

)
from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.decorators import use, UseType


class ModuleType(Enum):
    NONE = auto()
    LIMB = auto()
    IK_LIMB = auto()
    FK_LIMB = auto()
    IK_FK_LIMB = auto()

    ROOT = auto()
    EYE = auto()
    HAND = auto()
    FEET = auto()
    SPINE = auto()
    COG = auto()
    SCAPULA = auto()
    ARM = auto()
    LEG = auto()
    HEAD = auto()
    NECK = auto()


    WING = auto()

    SIMPLE = auto()


class BaseModule(ComposedComponent, ABC):
    """
    Base Module for every module
    It already contains:
        - a grp_name
        - a side_grp_name
        - an input
        - an output
        - a DO NOT TOUCH grp

    A module has to re-implement the following methods :
        - arrange_nodes(obj_to_parent)
        - set_input_and_output()
        - bind_jnts()

    Optional methods:
        - parent_to(parent, maintain_offset=True)
    """

    TYPE : ModuleType = ModuleType.NONE
    MODULE_PREFIX : str = "mdl_"
    INPUT_SUFFIX : str = "_input"
    OUTPUT_SUFFIX : str = "_output"
    SIDE_GROUP_PREFIX : str = "scale_"

    DO_NOT_TOUCH_GROUP_SUFFIX : str = "_DO_NOT_TOUCH"

    def __init__(self, name: str = None, config: Config = None, build=True):
        ComposedComponent.__init__(self, name=name, config=config)
        ABC.__init__(self)

        self.parents: list[BaseModule] = []
        self.children: list[BaseModule] = []

        self.is_mirrored = False

        if build:
            self._build()

    def _build(self):
        cmds.group(empty=True, name=self.side_grp_name)
        cmds.group(name=self.grp_name)

        cmds.group(name=self.dont_touch_grp, empty=True)
        cmds.parent(self.dont_touch_grp, self.grp_name)

        lct_in = cmds.spaceLocator(name=self.input)[0]
        lct_out = cmds.spaceLocator(name=self.output)[0]
        cmds.parent([lct_in, lct_out], self.side_grp_name)

    # region -- -- Properties
    @ComposedComponent.name.getter
    def name(self):
        return self.MODULE_PREFIX + super().name

    @ComposedComponent.side_suffix.setter
    def side_suffix(self, side):
        """
        Modifying the side_suffix of a module replaces the old side_suffix string with the new side_suffix in all names
        """
        if side not in self.SIDE_SUFFIXES and side not in (self.SIDE_SUFFIXES[0][-1], self.SIDE_SUFFIXES[1][-1]):
            return

        old_grp_name = self.grp_name
        old_size = self.side_suffix

        ComposedComponent.side_suffix.fset(self, side)

        hierarchy = get_hierarchy_list_from_root_node(old_grp_name)
        replace_in_names(hierarchy, old_size, side)

    @property
    def input(self):
        """The locator at the start of the module"""
        return self.LOCATOR_PREFIX + self.name + self.INPUT_SUFFIX

    @property
    def output(self):
        """The locator at the end of the module"""
        return self.LOCATOR_PREFIX + self.name + self.OUTPUT_SUFFIX

    @property
    def grp_name(self):
        return self.name + self.GROUP_SUFFIX

    @property
    def side_grp_name(self):
        return self.SIDE_GROUP_PREFIX + self.name + self.GROUP_SUFFIX

    @property
    def dont_touch_grp(self):
        return self.name + self.DO_NOT_TOUCH_GROUP_SUFFIX + self.GROUP_SUFFIX

    # endregion

    # region -- -- Methods
    def finalize(self):
        """
        Execute the module's methods set_input_and_output and arrange_nodes
        Method to execute after a new module has been created and parametrized
        """
        self.set_input_and_output()
        self.arrange_nodes([])
        self.bind_jnts([])

    def duplicate(self) -> ComposedComponent | None:
        opposite_side = self.opposite_side()
        if not opposite_side:
            return None

        # duplicate module grp and leave at place
        new_module_grp = cmds.duplicate(self.grp_name, rr=True, un=True)[0]

        # duplicate this module before modifying it
        new_module = copy.deepcopy(self)

        new_module.side_suffix = opposite_side

        # rename the new module group without the "1" added behind when duplicating
        cmds.rename(new_module_grp, self.grp_name)

        return new_module

    def mirror(self, axis=[-1, 1, 1]):
        scale = cmds.xform(self.side_grp_name, q=1, os=1, s=1, r=1)
        new_scale = [s * a for s, a in zip(scale, axis)]
        cmds.xform(self.side_grp_name, os=1, s=new_scale)

        self.is_mirrored = True

    @use(UseType.UNIQUE)
    def duplicate_and_mirror(self) -> ComposedComponent | None:
        if not self.side_suffix:
            print("Cannot duplicate and mirror without side suffix")
            return None

        new_module = self.duplicate()

        if not new_module:
            return None

        new_module.mirror()

        return new_module

    @use(UseType.UNIQUE | UseType.EXCLUDE_1)
    def set_parent_module(self, parent, maintain_offset=True):
        """
        Create parent / child relationship between modules
        By parent constraining this module's input to other module's output
        """
        if isinstance(parent, BaseModule):
            self.parents = [parent]
            parent.children += [self]
            cmds.parentConstraint(parent.output, self.input, mo=maintain_offset, weight=1)
            # testing scale
            cmds.scaleConstraint(parent.output, self.input, mo=True)
        else:
            print("Parent item", parent.name,"is not an instance of BaseModule, "
                  "couldn't find its output and parent this module", self.name,"to it")
            return

    @use(UseType.MULTIPLE)
    def set_child_module(self, child, maintain_offset=True):
        """
        Create parent / child relationship between modules
        By parent constraining this module's output to other module's input
        Internally it always uses the set_parent_module() of the child module
        """
        if isinstance(child, BaseModule):
            child.set_parent_module(self, maintain_offset=maintain_offset)
        else:
            print("Child item", child.name,"is not an instance of BaseModule, "
                  "couldn't find its input and parent it to this module", self.name)
            return

    @use(UseType.UNIQUE)
    def build_switch_parent_setup_on_ctl(self,
                                         parents_modules : list,
                                         switch_parent_ctl : Controller,
                                         parents_controllers : list[Controller] = [],
                                         parent_at_start = None,
                                         override_names = ["normal"]
                                         ):
        """
        Parent the switch_parent_ctl by creating a switch parent setup with chosen parents outputs and
        switch_parent_ctl : the target ctl on which constraint and attributes will be applied
        parents_modules : list of modules to be parents of the ctl
        parents_controllers : list of controllers to be parents of the ctl
        override_names : list of names to override enum_names for the parent attribute
        parent_at_start : set the starting enum names to this one e.g could be one ctl.name, or one of override_names
        """
        controller_names = [
            controller.name for controller in parents_controllers
            if isinstance(controller, Controller)
            ]
        parents_names = controller_names + [
            module._name for module in parents_modules
            if isinstance(module, BaseModule)
        ]

        parents_outputs = controller_names
        parents_outputs += [parent.output for parent in parents_modules]

        if parent_at_start:
            if isinstance(parent_at_start, BaseModule):
                parent_at_start = parent_at_start._name
            elif isinstance(parent_at_start, Controller):
                parent_at_start = parent_at_start.name

        create_switch_parent_setup_on_ctl(parents=parents_outputs,
                                          parents_names=parents_names,
                                          switch_ctl=switch_parent_ctl,
                                          name=self.name,
                                          override_names=override_names,
                                          parent_at_start=parent_at_start
                                          )


    def get_actual_component(self, component : BaseComponent | str) -> BaseComponent | str:
        """
        When this module has been mirrored, all names switched their side_suffix
        But internally, self.ctl_root.ame hasn't changed, and it's still the old side_suffix
        I don't think it is a better idea to dynamically creating all names everytime,
        Instead I implemented get_actual_component to get the name with the current and right side_suffix
        To use the method a function might be called after mirroring
        """
        if isinstance(component, str):
            if self.side_suffix not in component:
                component = component.replace(self.opposite_side(), self.side_suffix)
        elif self.side_suffix not in component.name:
            component.side_suffix = self.side_suffix
        return component

    # endregion

    # region -- Abstract Methods to be overridden
    @abstractmethod
    def arrange_nodes(self, obj_to_parent):
        """
        Parent all the elements under module input
        """
        for obj in obj_to_parent:
            cmds.parent(obj, self.input)

    @abstractmethod
    def set_input_and_output(self, input : str, output : str, input_pos=None, output_pos=None):
        """
        Positions lct input at the right place
        Positions and constraints lct output to the right place
        """
        if not input_pos:
            input_pos = cmds.xform(input, q=1, ws=1, t=1)
        cmds.xform(self.input, ws=1, t=input_pos)

        if not output_pos:
            output_pos = cmds.xform(output, q=1, ws=1, t=1)
        cmds.xform(self.output, ws=1, t=output_pos)

        cmds.parentConstraint(output, self.output, mo=False)
        # testing scale
        cmds.scaleConstraint(output, self.output, mo=True)

    @abstractmethod
    def bind_jnts(self, bind_jnts:list[str]) -> list[str]:
        """
        To be overridden by every module
        """
        create_set(bind_jnts, set_name="bind_jnts_set")
        return bind_jnts
    # endregion

