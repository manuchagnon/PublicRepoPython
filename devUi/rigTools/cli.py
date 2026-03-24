from devUi.rigTools.mainWindow import RigWindow
from devMaya.tool_launcher import launch_maya_tool

def run():
    launch_maya_tool(RigWindow)

if __name__ == '__main__':
    run()