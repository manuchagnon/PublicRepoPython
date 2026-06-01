from maya import cmds

"""
Functions that deals with :
creating base geometry for proxy mesh
creating bas geo for modeling

base geos are:
    - cube
    - cylinder
    - cone
    
"""


def create_base_cylinder(name="new",
                         at_origin=True,
                         height=1,
                         scale=1,
                         width_subdivisions=12,
                         open_sides=True,
                         height_subdivisions=1
                         ):
    geo = cmds.polyCylinder(name=name,
                      r=scale,
                      h=height*scale*2,
                      sx=width_subdivisions,
                      sy=height_subdivisions,
                      sz=1,
                      ax=[0, 1, 0],
                      rcp=0,
                      cuv=3,
                      ch=0)[0]

    if open_sides:
        faces_height = (height_subdivisions) * width_subdivisions
        max_faces = faces_height + width_subdivisions * 2
        print(faces_height, max_faces)
        cmds.delete(f"{geo}.f[{faces_height}:{max_faces}]")

    if at_origin:
        cmds.xform(geo, ws=1, t=[0, height * scale, 0])
        cmds.xform(geo, pivots=[0, 0, 0], worldSpace=True)
        cmds.makeIdentity(geo, apply=True, t=True)
