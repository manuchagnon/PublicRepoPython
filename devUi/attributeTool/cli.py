from devUi.attributeTool.mainWidget import AttributeWindow
from devMaya.tool_launcher import launch_maya_tool

def run():
    print("cli")
    window = AttributeWindow()
    print("cli2")
    launch_maya_tool(window)

if __name__ == '__main__':
    run()