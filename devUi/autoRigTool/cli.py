from devUi.autoRigTool.mainWindow import AutoRigWindow
from devMaya.tool_launcher import launch_maya_tool

def run():
    launch_maya_tool(AutoRigWindow)

if __name__ == '__main__':
    run()