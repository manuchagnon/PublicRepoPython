from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deal with :
mesh datas, 
vertices, edges, faces
"""

def find_closest_vertex_to_point(obj_name, point=(0, 0, 0)):
    """
    Function that takes a point in world space and a mesh and returns the closest mesh's vertex to the point and its index

    :param point: world space position, base pos is (0.0, 0.0, 0.0)
    :param obj_name: name of the mesh

    :return: closest mesh's vertex index, closest mesh's vertex position
    """

    # Initialize variables
    closest_vertex = None
    closest_vertex_position = None

    selection_list = om.MSelectionList() # instance the class MSelectionList

    try:
        selection_list.add(obj_name) # Get MDagPath of the chosen obj_name
        # dag_path = om.MDagPath() # instance the class dag_path
        # selection_list.getDagPath(0, dag_path)
        dag_path = selection_list.getDagPath(0)

        if dag_path.hasFn(om.MFn.kMesh): # check if the object is a mesh by testing to activate its funcction mesh
            fn_mesh = om.MFnMesh(dag_path)  # initialize mesh's functions

            vertex_iter = om.MItMeshVertex(dag_path)  # create an iterator (all vertices) to pass through all vertices of dag_path
            min_distance = float('inf')

            while not vertex_iter.isDone():

                vertex_position = vertex_iter.position(om.MSpace.kWorld) # Get the world position of the vertex

                # Distance between position and vertex position
                dx = vertex_position.x - point[0]
                dy = vertex_position.y - point[1]
                dz = vertex_position.z - point[2]
                distance_squared = (dx * dx + dy * dy + dz * dz)**0.5

                if distance_squared < min_distance: # Store the closest vertex
                    min_distance = distance_squared
                    closest_vertex = vertex_iter.index()
                    closest_vertex_position = (vertex_position.x, vertex_position.y, vertex_position.z)


                vertex_iter.next() # Next iteration for the while loop

            return closest_vertex, min_distance
        else:
            print(f'{obj} is not a mesh')
            return None

    except RuntimeError as e:
        print(f"Erreur lors du traitement de l'objet : {e}")
        return None

def find_furthest_vertex_to_point(obj_name, point=(0, 0, 0)):
    """
    Function that takes a point in world space and a mesh and returns the furthest mesh's vertex to the point and its index

    :param point: world space position, base pos is (0.0, 0.0, 0.0)
    :param obj_name: name of the mesh

    :return: furthest mesh's vertex index, furthest mesh's vertex position
    """

    # Initialize variables
    furthest_vertex = None
    furthest_vertex_position = None

    selection_list = om.MSelectionList() # instance the class MSelectionList

    try:
        selection_list.add(obj_name) # Get MDagPath of the chosen obj_name
        # dag_path = om.MDagPath() # instance the class dag_path
        # selection_list.getDagPath(0, dag_path)
        dag_path = selection_list.getDagPath(0)

        if dag_path.hasFn(om.MFn.kMesh): # check if the object is a mesh by testing to activate its funcction mesh
            fn_mesh = om.MFnMesh(dag_path)  # initialize mesh's functions

            vertex_iter = om.MItMeshVertex(dag_path)  # create an iterator (all vertices) to pass through all vertices of dag_path
            max_distance = 0

            while not vertex_iter.isDone():

                vertex_position = vertex_iter.position(om.MSpace.kWorld) # Get the world position of the vertex

                # Distance between position and vertex position
                dx = vertex_position.x - point[0]
                dy = vertex_position.y - point[1]
                dz = vertex_position.z - point[2]
                distance_squared = (dx * dx + dy * dy + dz * dz)**0.5

                if distance_squared > max_distance: # Store the furthest vertex
                    max_distance = distance_squared
                    furthest_vertex = vertex_iter.index()
                    furthest_vertex_position = (vertex_position.x, vertex_position.y, vertex_position.z)

                vertex_iter.next() # Next iteration for the while loop

            return furthest_vertex, max_distance
        else:
            print(f'{obj} is not a mesh')
            return None

    except RuntimeError as e:
        print(f"Erreur lors du traitement de l'objet : {e}")
        return None


def run():
    import maya.cmds as cmds

    locator = "locator1"
    point = cmds.xform(locator, ws=1, q=1, t=1)

    for sl in cmds.ls(sl=True):

        closest_vertex, closest_vertex_position = find_closest_vertex_to_point(point, sl)

        if not cmds.objExists(f"lct_{sl}"):
            cmds.spaceLocator(name=f"lct_{sl}")
            cmds.xform(f"lct_{sl}", ws=1, t=closest_vertex_position)
        else:
            cmds.xform(f"lct_{sl}", ws=1, t=closest_vertex_position)

        if closest_vertex:
            print(
                f"Le vertex le plus proche de {locator} est l'index {closest_vertex} à la position {closest_vertex_position}.")
        else:
            print("Aucun mesh sélectionné ou aucun vertex trouvé.")


if __name__ == '__main__':
    run()