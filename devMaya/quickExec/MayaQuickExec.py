import traceback
from maya import cmds as cmds

def run():
    print("-- quick exec run --\n")
    try:
        # exec(open("C:\Users\chagnon\PycharmProjects\myRepo\rigging\utils\find_closest_point_on_a_mesh.py").read())
        exec(open(r"C:\Users\Utilisateur\AppData\Roaming\JetBrains\PyCharm2025.3\scratches\scratch_controller_test.py").read())
    except Exception as e:
        raise Exception(traceback.format_exc())

def finish():
    print("\n-- quick exec finish --")
