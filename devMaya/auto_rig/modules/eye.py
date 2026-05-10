
from base import BaseModule, ModuleType

class Eye(BaseModule):

    TYPE = ModuleType.EYE

    def __init__(self, vtx_eyelid_up: list[str], vtx_eyelid_bot: list[str], vtx_eyelid_follow_up: list[str], vtx_eyelid_follow_bot: list[str], non_spherical=False):
        super().__init__(self)

        self._build_eye()
        self.set_input_and_output()
        self.arrange_nodes()


    def set_input_and_output(self):
        self.input = self._ctl_chain[0]
        self.output = self._ctl_chain[-1]


    def arrange_nodes(self):
        obj_to_parent = [
        ]
        super().arrange_nodes(obj_to_parent)
