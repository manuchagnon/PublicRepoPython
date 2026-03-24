from Qt import QtWidgets

def launch_maya_tool(widget: QtWidgets.QWidget):
    import sys

    try:
        from maya import cmds
        in_maya = not cmds.about(batch=True)
    except:
        in_maya = False

    # Set a custom palette for the app
    try:
        import qdarktheme
        qdarktheme.setup_theme()
    except ImportError:
        print("qdarktheme not found, using default theme")


    # Launch
    if in_maya:
        window = widget()
        window.show(dockable=True, area="right", floating=True)
    else:
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)

        window = widget()
        window.show()
        sys.exit(app.exec())