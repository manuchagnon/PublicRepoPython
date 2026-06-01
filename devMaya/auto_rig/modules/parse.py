from maya import cmds

from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.modules.base import BaseModule

class ParseModule(BaseModule):
    """
    Used when you want to duplicate a module already in the scene
    e.g when you modified controllers, and you want to mirror the module

    TO DO:
    Make it deduct its bind_jnts, its parent output
    """

    INFOS = """
    method : parse_module_grp(module_grp : str) -> BaseModule | None: 
    Try to parse the module from provided module base grp
    - A module base group should be constructed as "self.MODULE_SUFFIX + self.name + self.GROUP_SUFFIX" (e.g : mdl_arm_L_grp)
    - It should be at the top of the outliner hierarchy
    
    method : parse_from_child_module(child_input: str) -> BaseModule | None:
    Try to parse the child module from provided child input
    
    Deduct:
    - its side_suffix
    - its scale grp
    - its input and output

    Don't deduct :
    - its type


    """

    def __init__(self):
        print("Select a module base group and execute method 'parse_module_grp(module_grp : str)'")

    def parse_from_module_grp(self, module_grp: str) -> BaseModule | None:
        """
        Try to parse a module from provided module grp
        """
        result = self._tests_module_grp(module_grp)

        if not result:
            self._print_error_message()
            return None
        else:
            self._print_success_message(result.name)
            return result

    def _tests_module_grp(self, module_grp: str) -> BaseModule | None:

        # Series of tests on the name provided
        if not isinstance(module_grp, str):
            print("Provided data is not a string")
            return None

        if not module_grp.startswith(self.MODULE_PREFIX):
            print(f"Name does not start with '{self.MODULE_PREFIX}'")
            return None

        if not module_grp.endswith(self.GROUP_SUFFIX):
            print(f"Name does not end with '{self.GROUP_SUFFIX}'")
            return None

        if not cmds.objExists(module_grp):
            print(f"Module base group name '{module_grp}' does not exist in scene")
            return None

        module_name = module_grp.split(self.GROUP_SUFFIX)[0]

        name = module_name.split(self.MODULE_PREFIX)[-1]
        module_test = BaseModule(name=name, build=False)
        # self._name = module_name.split(self.MODULE_PREFIX)[-1]

        side_grp_name = self.SIDE_GROUP_PREFIX + module_grp
        if not cmds.objExists(side_grp_name):
            print(f"Module scale group '{side_grp_name}' does not exist in scene")
        else:
            print(f"- side_grp_name : {side_grp_name}")
        # self.side_grp_name = side_grp_name

        input, output = self.LOCATOR_PREFIX + module_name + self.INPUT_SUFFIX, self.LOCATOR_PREFIX + module_name + self.OUTPUT_SUFFIX
        if not all([cmds.objExists(input), cmds.objExists(output)]):
            print(f"Module input '{input}' and output '{output}' dont exist in scene")
            return None
        else:
            print(f"- input : {input}, output : {output}")
        # self.input, self.output = input, output

        for side in self.SIDE_SUFFIXES:
            if side in module_name:
                print(f"- side_suffix : {side}")
                side_suffix = side
                break
            else:
                print(f"- side_suffix : None")
                side_suffix = None
        # self._side = side_suffix

        return module_test

    def parse_from_child_module(self, child_input: str) -> BaseModule | None:
        """
        Try to parse a module from provided child input
        """
        result = self._tests_module_grp(child_input)

        if not result:
            self._print_error_message()
            return None
        else:
            self._print_success_message(result.name)
            return result

    def _tests_child_input(self, child_input: str) -> BaseModule | None:
        return None


    def infos(self):
        print(self.INFOS)


    def _print_error_message(self):
        print(
            "\tERROR : Cannot find module with provided data\n\tPlease select the base group of the module and try again")

    def _print_success_message(self, module_name: str):
        print(f"\tSUCCESS : Parsed module '{module_name}'")
