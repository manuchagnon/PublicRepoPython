from devUi.skinTools.mainWindow import SkinWindow
from devMaya.tool_launcher import launch_maya_tool

def run():
    launch_maya_tool(SkinWindow)

if __name__ == '__main__':
    run()