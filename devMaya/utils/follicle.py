from maya import cmds
import maya.api.OpenMaya as om

from .controller import create_FK_ctl

"""
Functions that deals with :
creating follicle on surface
"""



def create_follicle_on_surface(
        surface,
        flc_on_u,
        flc_on_v,

        flc_param_u_start = 0,
        flc_param_u_end = 1,
        flc_param_u_offset = 0,

        flc_param_v_start = 0,
        flc_param_v_end = 1,
        flc_param_v_offset = 0
        ):
    """
    Create follicles on a surface with custom parameters
    """
