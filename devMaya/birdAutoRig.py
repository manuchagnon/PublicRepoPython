from maya import cmds
import maya.api.OpenMaya as om
from utils.api import *

# region Bird Auto RIG

class RigParameters:

    def __init__(self, jnt_orient="xyz", name_space="BIRD:"):
        self._JNT_ORIENT = jnt_orient
        self._NAME_SPACE = name_space

class LeftSide(RigParameters):

    def __init__(self, suffix="L"):
        super().__init__()
        self._SUFFIX = suffix

class FeatherRig(LeftSide):

    def __init__(self, feather_mesh, jnt_main=None, jnt_amount=4, main_locator="locator1"):
        super().__init__()

        self._jnt_main = jnt_main
        self._jnt_amount = jnt_amount
        self._jnt_list = []
        self._main_locator = main_locator
        self._feather_mesh = feather_mesh

    def create_feather_rig(self):
        if not self._feather_mesh:
            print("No mesh selected")
            return None

        closest_index, closest_pos = find_closest_vertex_to_point(self._feather_mesh,cmds.xform(self._main_locator, ws=1, q=1, t=1))

        furthest_index, furthest_pos = find_furthest_vertex_to_point(self._feather_mesh,cmds.xform(self._main_locator, ws=1, q=1, t=1))

        cmds.select(clear=1)
        jnt_root = cmds.joint(name=f'jnt_{self._feather_mesh}00_{self._SUFFIX}')
        pos = cmds.xform(f'{self._feather_mesh}.vtx[{closest_index}]', q=1, ws=1, t=1)
        cmds.xform(jnt_root, ws=1, t=pos)

        cmds.select(clear=1)
        jnt_end = cmds.joint(name=f'jnt_{self._feather_mesh}01_{self._SUFFIX}')
        pos = cmds.xform(f'{self._feather_mesh}.vtx[{furthest_index}]', q=1, ws=1, t=1)
        cmds.xform(jnt_end, ws=1, t=pos)
        cmds.parent(jnt_end, jnt_root)

        cmds.joint(jnt_root, e=1, oj=self._JNT_ORIENT, secondaryAxisOrient="yup", ch=1, zso=1)
        cmds.joint(jnt_end, e=1, oj="none", ch=1, zso=1)

        self._jnt_list.append(jnt_root)
        self._jnt_list.append(jnt_end)

        return jnt_root

    def create_controllers(self):
        self._controllers = create_FK_ctl(self._jnt_list, message = self._feather_mesh, parented=True)

    def skin_feathers(self):
        cmds.skinCluster(self._jnt_list, self._feather_mesh, mi=3)

# endregion

def run():
    # select several meshes and build feather rig setup
    mesh_list = cmds.ls(sl=1)

    group = cmds.group(name="feathers_grp", empty=1)

    # will execute the feather rig module on selected meshes
    feathers_list = []
    for mesh in mesh_list:
        feather_rig = FeatherRig(mesh)
        joint = feather_rig.create_feather_rig()
        if feather_rig:
            cmds.parent(joint, group)
        feather_rig.create_controllers()
        feather_rig.skin_feathers()

    cmds.select(mesh_list)


if __name__ == '__main__':
    print("="*100)
    run()
    print("Finished execution")
    print("-"*100)
