from maya import cmds

import copy
from enum import Enum, auto

from ..component.base import BaseComponent
from devMaya.utils.api import get_hierarchy_list_from_root_node, replace_in_names, create_set
from devMaya.auto_rig.configs.config import Config

class ModuleType(Enum):

    NONE = auto()
    LIMB = auto()
    IK_LIMB = auto()
    FK_LIMB = auto()
    IK_FK_LIMB = auto()

    ROOT = auto()
    COG = auto()
    SPINE = auto()
    ARM = auto()
    HAND = auto()
    FEET = auto()
    EYE = auto()

    WING = auto()

    SIMPLE = auto()

class BaseModule(BaseComponent):

    """
    Base Module for every modules
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

    TYPE = ModuleType.NONE
    MODULE_PREFIX = "mdl_"
    INPUT_SUFFIX = "_input"
    OUTPUT_SUFFIX = "_output"
    SIDE_GROUP_PREFIX = "scale_"

    DO_NOT_TOUCH_GROUP_SUFFIX = "_DO_NOT_TOUCH"

    def __init__(self, name: str=None, config: Config=None, build=True):
        super().__init__(name=name, config=config)
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

    @BaseComponent.name.getter
    def name(self):
        return self.MODULE_PREFIX + super().name

    @BaseComponent.side_suffix.setter
    def side_suffix(self, side):
        if side not in self.SIDE_SUFFIXES and side not in (self.SIDE_SUFFIXES[0][-1], self.SIDE_SUFFIXES[1][-1]):
            return

        old_grp_name = self.grp_name
        old_size = self.side_suffix

        BaseComponent.side_suffix.fset(self, side)

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

    def duplicate(self) -> BaseComponent | None:
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

    def duplicate_and_mirror(self) -> BaseComponent | None:
        if not self.side_suffix:
            print("Cannot duplicate and mirror without side suffix")
            return None

        new_module = self.duplicate()

        if not new_module:
            return None

        new_module.mirror()

        return new_module

    def arrange_nodes(self, obj_to_parent):
        """
        Parent all the elements under module input
        """
        for obj in obj_to_parent:
            cmds.parent(obj, self.input)

    def set_input_and_output(self):
        """
        Position lct in to the right place
        Position and constraints lct out to the right place
        """
        # e.g position input and output
        # cmds.xform(self.input, ws=1, t=self.fk_limb.ctls[0].pos)
        # cmds.xform(self.output, ws=1, t=self.fk_limb.ctls[-1].pos)

        # e.g constraint ouput
        # cmds.parentConstraint(self.jnts[-1], self.output, mo=False)[0]
        pass

    def parent_module(self, child, maintain_offset=True):
        """
        Create parent / child relationship between modules
        By parent constraining this module's output to other module's input
        """
        if not isinstance(child, BaseModule):
            print("Child item is not an instance of BaseModule, "
                  "couldn't find its input and parent it to this module")
            return

        self.child = child
        cmds.parentConstraint(self.output, child.input, mo=maintain_offset, weight=1)

    def bind_jnts(self) -> list:
        """
        To be overridden by every module
        """
        create_set([], set_name="bind_jnts_set")
        return []
