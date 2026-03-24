from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating joints
getting skinned joints
getting mirrored version of joints
creating, editing skin clusters
adding join to skin cluster
"""

def create_jnt(obj : str, parent = 1, suffix=""):
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
    cmds.select(clear=1)

    if parent == 1:
        cmds.parent(jnt, obj)
        cmds.xform(jnt, t=[0, 0, 0], ro=[0, 0, 0])

    if parent == 2:
        obj_parent = cmds.listRelatives(obj, parent=True, fullPath=1)[0]
        cmds.parent(jnt, obj_parent)
        cmds.xform(jnt, t=[0, 0, 0], ro=[0, 0, 0])
        cmds.parent(obj, jnt)

    return jnt

def create_jnts(obj_list = [], parent = 1, suffix="", in_autorig=True) -> list[str]:
    """
    Create multiple joints
    """
    if obj_list == []: # if no list is provided, use the selected objects ([] if no selection)
        obj_list = cmds.ls(sl=1)

    jnt_created = []

    for obj in obj_list:
        jnt = create_jnt(obj, parent = parent, suffix=suffix)
        jnt_created.append(jnt)

    if not in_autorig:
        cmds.select(jnt_created)

    return jnt_created

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
