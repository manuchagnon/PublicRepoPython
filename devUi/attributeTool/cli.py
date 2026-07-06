from devUi.attributeTool.mainWidget import AttributeWindow
from devMaya.tool_launcher import launch_maya_tool

def run():
    launch_maya_tool(AttributeWindow)

if __name__ == '__main__':
    run()