from maya import cmds
import maya.api.OpenMaya as om

from devUtils.maths import remap_value

"""
Functions that deals with :
creating follicle on surface
"""



def create_flc_on_surface(
        surface : str = None,
        flc_on_u = 1,
        flc_on_v = 1,

        flc_param_u_start = 0,
        flc_param_u_end = 1,
        flc_param_u_offset = 0,

        flc_param_v_start = 0,
        flc_param_v_end = 1,
        flc_param_v_offset = 0
        ) -> list[str]:
    """
    Create follicles on a surface with custom parameters
    """

    if not surface:
        try:
            surface = cmds.ls(sl=1)[0]
        except:
            return []

        shapes = cmds.listRelatives(surface, children=1, shapes=1)
        shp = [shp for shp in shapes if not "Orig" in shp][0]
        if not cmds.objectType(shp) == "nurbsSurface":
            print("couldn't create follicles because", surface, "type is not 'nurbsSurface'")
            return []

    if "srf_" in surface:
        srf_name = surface.split("srf_")[1]
    else:
        srf_name = surface

    flc_created = []
    flc_grp = cmds.group(name=f'flc_{srf_name}_grp', empty=1)

    for i_u in range(flc_on_u):
        for i_v in range(flc_on_v):
            if flc_on_u > 1: # if there is more than one flc
                parameter_u = i_u / (flc_on_u - 1)
    
                parameter_u = remap_value(parameter_u, 0, 1, flc_param_u_start, flc_param_u_end)
    
                if flc_param_u_offset: # if there is an offset provided
                    parameter_u += flc_param_u_offset
    
                if parameter_u > 1:
                    parameter_u -= 1
                    if f"{flc_created[-1]}.parameterU" == 1:
                        parameter_u = 0

            elif flc_on_u == 1: # if there is one flc
                if flc_param_u_offset: # if there is an offset provided
                    parameter_u = flc_param_u_offset
                else:
                    parameter_u = 0.5

            if flc_on_v > 1:
                parameter_v = i_v / (flc_on_v - 1)

                parameter_v = remap_value(parameter_v, 0, 1, flc_param_v_start, flc_param_v_end)
    
                if flc_param_v_offset:
                    parameter_v += flc_param_v_offset

                if parameter_v > 1:
                    parameter_v += -1
                    if f"{flc_created[-1]}.parameterV" == 1:
                        parameter_v = 0

            elif flc_on_v == 1:
                if flc_param_v_offset:
                    parameter_v = flc_param_v_offset
                else:
                    parameter_v = 0.5


            flc_index = len(flc_created)
    
            # Create follicle node with its shape and its transform
            flc_shape = cmds.createNode("follicle", name=f"flc_{srf_name}_{flc_index}Shape")
    
            flc_transform = cmds.listRelatives(flc_shape, parent=1)[0]
            cmds.rename(flc_transform, f"flc_{srf_name}_{flc_index}")
            flc_transform = f"flc_{srf_name}_{flc_index}"
    
            cmds.connectAttr(f"{surface}.worldSpace[0]", f"{flc_shape}.inputSurface", f=1)
            cmds.connectAttr(f"{surface}.worldMatrix[0]", f"{flc_shape}.inputWorldMatrix", f=1)
            cmds.connectAttr(f"{flc_shape}.outRotate", f"{flc_transform}.rotate", f=1)
            cmds.connectAttr(f"{flc_shape}.outTranslate", f"{flc_transform}.translate", f=1)
    
            cmds.setAttr(f"{flc_shape}.parameterU", parameter_u)
            cmds.setAttr(f"{flc_shape}.parameterV", parameter_v)
    
            cmds.parent(flc_transform, flc_grp) # append to follicle group
            flc_created.append(flc_transform)
    
    return flc_created
