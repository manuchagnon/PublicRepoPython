from maya import cmds
import maya.api.OpenMaya as om

from devMaya.utils.controller import get_ctl_shapes
from devMaya.utils.nurbs_curve import distribute_lct_on_crv
from devMaya.utils.name import get_name_part, rename_and_increment
from devMaya.utils.position import lerp_pos
from devUi.utils.colors import Colors

from devUtils.maths import remap_value

"""
Functions that deals with :
creating joints
getting skinned joints
getting mirrored version of joints
creating, editing skin clusters
adding join to skin cluster
"""

def create_jnt(obj : str, parent = 1, radius=1, suffix=""):
    """
    Create a joint under the selected object
    parent:
        0 == no parenting
        1 == jnt is parented to obj
        2 == jnt is parent of obj
    suffix:
    """

    if suffix != "" and "_" not in suffix:
        suffix = "_" + suffix

    cmds.select(clear=1)

    if "_" in str(obj):
        obj_name = str(obj).split('_', 1)[1]
    else:
        obj_name = obj

    jnt = cmds.joint(n=f'jnt_{obj_name}{suffix}')
    cmds.setAttr(f"{jnt}.radius", radius)
    cmds.select(clear=1)

    if parent == 0:
        cmds.matchTransform(jnt, obj)
        cmds.makeIdentity(jnt, apply=1, t=1, r=1, s=1)

    elif parent == 1:
        cmds.parent(jnt, obj)
        cmds.xform(jnt, t=[0, 0, 0], ro=[0, 0, 0])
        cmds.makeIdentity(jnt, apply=1, t=1, r=1, s=1)

    elif parent == 2:
        obj_parent = cmds.listRelatives(obj, parent=True, fullPath=1)[0]
        cmds.parent(jnt, obj_parent)
        cmds.xform(jnt, t=[0, 0, 0], ro=[0, 0, 0])
        cmds.parent(obj, jnt)

    return jnt

def create_jnts(obj_list = [], parent = 1, suffix="", radius=1, in_autorig=True) -> list[str]:
    """
    Create multiple joints
    """
    if obj_list == []: # if no list is provided, use the selected objects ([] if no selection)
        obj_list = cmds.ls(sl=1)

    jnt_created = []

    for obj in obj_list:
        jnt = create_jnt(obj, parent = parent, radius=radius, suffix=suffix)
        jnt_created.append(jnt)

    if not in_autorig:
        cmds.select(jnt_created)

    return jnt_created

def reset_jnt_orient(jnt):
    for axis in ["X", "Y", "Z"]:
        cmds.setAttr(f"{jnt}.jointOrient{axis}", 0)

def reset_jnts_orient(jnt_list):
    for jnt in jnt_list:
        reset_jnt_orient(jnt)


def subdivide_jnt_chain(jnt_chain: list[str], in_between_jnt: int=1, interpolation=0) -> list[str]:
    """
    Create one or more joints between each joint of a joint chain to "subdivide" it
    TO DO:
    Implement interpolation behavior = smooth for smoothing joint chains
    """
    jnt_length = len(jnt_chain)
    if jnt_length <= 1:
        return jnt_chain

    # Renaming the whole chain so new names don't bug
    # inverted_jnt_chain = []
    # for i in range(jnt_length):
    #     jnt = jnt_chain[::-1][i]
    #
    #     new_name = jnt + "temp"
    #     cmds.rename(jnt, new_name)
    #
    #     inverted_jnt_chain.append(new_name)

    # inverted_jnt_chain.reverse()

    # Behavior for linear interpolation
    if interpolation == 0:
        new_jnt_chain = []
        for i in range(jnt_length):
            jnt = jnt_chain[i]
            new_jnt_chain.append(jnt)

            if i == jnt_length-1:
                break

            next_jnt = jnt_chain[i + 1]
            for index_in_between in range(in_between_jnt):
                cmds.select(clear=1)
                new_jnt = cmds.joint(name=f"jnt_temp_{i}+{index_in_between+1}")

                # cmds.delete(cmds.pointConstraint(jnt, next_jnt, new_jnt, mo=False))
                factor = 1 / (in_between_jnt + 1) * (index_in_between+1)
                pos = lerp_pos(jnt, next_jnt, factor=factor)
                cmds.xform(new_jnt, ws=1, t=pos)

                cmds.delete(cmds.orientConstraint(jnt, new_jnt, mo=False))

                cmds.parent(new_jnt, new_jnt_chain[-1])
                new_jnt_chain.append(new_jnt)


            cmds.parent(next_jnt, new_jnt_chain[-1])

        name_part = get_name_part(new_jnt_chain[0])
        new_jnt_chain = rename_and_increment(new_jnt_chain, base_name=name_part+"_")

        return new_jnt_chain

def create_jnt_chain(obj_list = [], suffix="", orient_joint="xyz", secondary_axis="yup", in_autorig=True) -> list[str]:
    """
    Create a joint chain
    """
    if obj_list == []: # if no list is provided, use the selected objects ([] if no selection)
        obj_list = cmds.ls(sl=1)

    jnt_created = []

    for i, obj in enumerate(obj_list):
        jnt = create_jnt(obj, parent=0, suffix=suffix)
        jnt_created.append(jnt)

        if i > 0:
            cmds.parent(jnt, jnt_created[i-1])

    cmds.joint(jnt_created[0], e=1, oj=orient_joint, secondaryAxisOrient=secondary_axis, ch=1, zso=1)
    cmds.joint(jnt_created[-1], e=1, oj="none", ch=1, zso=1)

    if not in_autorig:
        cmds.select(jnt_created)

    return jnt_created

def create_jnt_chain_on_crv(crv: str=None, jnt_amount: int = 5, suffix="", orient_joint="xyz", secondary_axis="yup", in_autorig=True):
    if not crv:
        crv = cmds.ls(sl=1)[0]
    shape = get_ctl_shapes(crv)
    if not shape:
        return

    lcts = distribute_lct_on_crv(crv=crv, inst_number=jnt_amount, constrained=False)
    create_jnt_chain(obj_list=lcts, suffix=suffix, orient_joint=orient_joint, secondary_axis=secondary_axis, in_autorig=in_autorig)
    cmds.delete(lcts)

def get_skin_cluster(obj=None):
    if not obj:
        obj = cmds.ls(sl=1)[0]

    skin_cluster = cmds.ls(cmds.listHistory(obj), type="skinCluster")
    if skin_cluster:
        return skin_cluster[0]
    else:
        return None


def skinned_joints(obj=None):
    if not obj:
        obj = cmds.ls(sl=1)[0]
    if not obj:
        cmds.warning("First Select an Object or enter its name in the box")
        return False

    skin_cluster = get_skin_cluster(obj)

    if not skin_cluster:
        cmds.warning(f"Selected object doesn't have a SkinCluster attached to it")
        return False

    # "joints = (jnt for jnt in cmds.listConnections(source=True, type="joint"))
    joints = cmds.ls(cmds.listHistory(obj), type="joint")

    cmds.select(joints)

    return joints


def mirrored_joints(joints, source_suffix="_L", target_suffix="_R"):
    no_mirror_joints = []
    mirror_joints = []

    for joint in joints:
        if source_suffix not in joint:
            no_mirror_joints.append(joint)
            continue
        else:
            mirror_joint = joint.replace(source_suffix, target_suffix, 1)
            if cmds.objExists(mirror_joint):
                mirror_joints.append(mirror_joint)
            else:
                no_mirror_joints.append(joint)

                cmds.select(mirror_joints)

    return mirror_joints, no_mirror_joints


def unskin_joints(joints, skin_cluster=None, obj=None):
    if not joints:
        print("No Joint provided")
        return False

    if not skin_cluster and not obj:
        print("Either provide a SkinCluster or an Object with SkinClusster")
        return False
    elif obj:
        skin_cluster = get_skin_cluster(obj)
        if skin_cluster:
            cmds.skinCluster(obj, e=1, removeInfluence=joints)
        else:
            print("The Object doesn't have a SkinCluster attached to it")
            return False
    elif skin_cluster:
        cmds.skinCluster(skin_cluster, joints, e=1, removeInfluence=joints)

    return True


def skin_joints(joints, skin_cluster=None, obj=None, max_inf=3, weight=0.0, remove_influence=False):
    if not joints:
        print("No Joint provided")
        return False

    if not skin_cluster and not obj:
        print("Either provide a SkinCluster or an Object with SkinCluster")
        return False

    elif skin_cluster:
        if remove_influence:
            for joint in joints:
                cmds.skinCluster( skin_cluster, e=1, mi=max_inf, weight=weight, ps=0, ns=10, lw=True, ri=joint)
        else:
            for joint in joints:
                cmds.skinCluster( skin_cluster, e=1, addInfluence=joint, mi=max_inf, ug=0, weight=weight, ps=0, ns=10, lw=True)

    elif obj:
        skin_cluster = get_skin_cluster(obj)
        if skin_cluster:
            if remove_influence:
                for joint in joints:
                    cmds.skinCluster( skin_cluster, e=1, mi=max_inf, weight=weight, ps=0, ns=10, lw=True, ri=joint)
            else:
                for joint in joints:
                    cmds.skinCluster( skin_cluster, e=1, addInfluence=joint, ug=0, mi=max_inf, weight=weight, ps=0, ns=10, lw=True)

        else:
            cmds.skinCluster(joints, obj, mi=max_inf, weight=weight) # create new skin cluster

    return True

def set_jnt_color(jnt, color : Colors | str):
    cmds.setAttr(f"{jnt}.overrideEnabled", 1)
    cmds.setAttr(f"{jnt}.overrideRGBColors", 1)

    color = Colors.get_color(color)

    color = [remap_value(c, 0, 255, 0, 1) if c > 1 else 0 for c in color]

    for i, channel in enumerate(Colors.CHANNELS):
        cmds.setAttr(f"{jnt}.overrideColor{channel}", color[i])


def create_jnt_chain_rotate_blending(jnt_chain_parent_1:list[str],
                              jnt_chain_parent_2:list[str],
                              jnt_chain_target:list[str],
                              attribute_blender:str,
                              suffix=""
                              ):
    for joint_IK, joint_FK, joint_blend in zip(jnt_chain_parent_1, jnt_chain_parent_2, jnt_chain_target):

        # create rotate pair_blend
        pair_blend = cmds.createNode("pairBlend", name=f'{joint_blend}_pb')

        # connect rotates to pair_blend
        cmds.connectAttr(f'{joint_FK}.rotate', f'{pair_blend}.inRotate1')
        cmds.connectAttr(f'{joint_IK}.rotate', f'{pair_blend}.inRotate2')
        cmds.connectAttr(f'{pair_blend}.outRotate', f'{joint_blend}.rotate')

        # connect switch attribute to pair_blend weight
        cmds.connectAttr(attribute_blender, f'{pair_blend}.weight', f=1)


def create_jnt_chain_translate_blending(jnt_chain_parent_1:list[str],
                              jnt_chain_parent_2:list[str],
                              jnt_chain_target:list[str],
                              attribute_blender:str,
                              suffix=""
                              ):
    for joint_IK, joint_FK, joint_blend in zip(jnt_chain_parent_1, jnt_chain_parent_2, jnt_chain_target):
        # create translate blend color
        blend_colors = cmds.createNode("blendColors", name=f'{joint_blend}_bc')

        # connect translates to pair_blend
        cmds.connectAttr(f'{joint_FK}.translate', f'{blend_colors}.color2')
        cmds.connectAttr(f'{joint_IK}.translate', f'{blend_colors}.color1')
        cmds.connectAttr(f'{blend_colors}.output', f'{joint_blend}.translate')

        # connect switch attribute to pair_blend weight
        cmds.connectAttr(attribute_blender, f'{blend_colors}.blender', f=1)


def create_jnt_chain_blending(jnt_chain_parent_1:list[str],
                              jnt_chain_parent_2:list[str],
                              jnt_chain_target:list[str],
                              attribute_blender:str,
                              suffix=""
                              ):
    """
    Create a setup of blending two joint chains into one
    Used for blending Ik and Fk joint chains
    """
    create_jnt_chain_translate_blending(jnt_chain_parent_1=jnt_chain_parent_1,
                              jnt_chain_parent_2=jnt_chain_parent_2,
                              jnt_chain_target=jnt_chain_target,
                              attribute_blender=attribute_blender,
                              suffix=suffix)
    create_jnt_chain_rotate_blending(jnt_chain_parent_1=jnt_chain_parent_1,
                              jnt_chain_parent_2=jnt_chain_parent_2,
                              jnt_chain_target=jnt_chain_target,
                              attribute_blender=attribute_blender,
                              suffix=suffix)

