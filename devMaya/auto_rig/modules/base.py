from maya import cmds

from enum import Enum, auto

from ..component.base import BaseComponent
from devMaya.utils.api import get_hierarchy_list_from_root_node, replace_in_names

class ModuleType(Enum):

    NONE = auto()
    LIMB = auto()
    IK_LIMB = auto()
    FK_LIMB = auto()
    IK_FK_LIMB = auto()

    GLOBAL = auto()
    COG = auto()
    SPINE = auto()
    ARM = auto()
    HAND = auto()
    FEET = auto()
    EYE = auto()

class BaseModule(BaseComponent):

    """
    Base Module for every modules
    It already contains:
        - a grp_name
        - a side_grp_name
        - an input
        - an output


    A module has to implement the following methods :
        - arrange_nodes(obj_to_parent)
        - set_input_and_output()

    Optional methods:
        - parent_to(parent, maintain_offset=True)
    """

    TYPE = ModuleType.NONE
    MODULE_PREFIX = "mdl_"
    INPUT_SUFFIX = "_input"
    OUTPUT_SUFFIX = "_output"
    SIDE_GROUP_PREFIX = "scale_"

    def __init__(self, name: str=None):
        super().__init__(name=name)

        self._build()

    def _build(self):
        cmds.group(empty=True, name=self.side_grp_name)
        cmds.group(name=self.grp_name)

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
        # locator at the start of the module
        return self.LOCATOR_PREFIX + self.name + self.INPUT_SUFFIX

    @property
    def output(self):
        # locator at the end of the module
        return self.LOCATOR_PREFIX + self.name + self.OUTPUT_SUFFIX

    @property
    def grp_name(self):
        return self.name + self.GROUP_SUFFIX

    @property
    def side_grp_name(self):
        return self.SIDE_GROUP_PREFIX + self.name + self.GROUP_SUFFIX

    def duplicate_and_mirror(self):
        if not self.side_suffix:
            print("no side suffix")
            return

        # duplicate module and leave at place
        new_module_grp = cmds.duplicate(self.grp_name, rr=True, un=True)[0]
        old_module_grp_name = self.grp_name

        # change this module side and rename
        side_list = self.SIDE_SUFFIXES[:]
        side_list.pop(self.SIDE_SUFFIXES.index(self.side_suffix))
        new_size = side_list[0]
        self.side_suffix = new_size

        # mirror this module
        self.mirror() # mirror

        # rename the new module group with the "1" added behind when duplicating
        cmds.rename(new_module_grp, old_module_grp_name)

    def mirror(self, axis=[-1, 1, 1]):
        if not self.side_suffix:
            return

        scale = cmds.xform(self.side_grp_name, q=1, os=1, s=1, r=1)
        new_scale = [scale[i] * axis[i] for i in range(len(axis))]
        cmds.xform(self.side_grp_name, os=1, s=new_scale)

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

    def parent_to(self, parent, maintain_offset=True):
        """
        Create child / parent relationship between modules by parent constraining them
        """
        if not isinstance(parent, BaseModule):
            return

        self.parent = parent
        cmds.parentConstraint(parent.output, self.input, mo=maintain_offset, weight=1)

