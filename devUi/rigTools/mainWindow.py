import sys

from maya import cmds

from PySide6 import QtCore, QtGui, QtWidgets

from controllerWidget import ControllerWidget
from follicleWidget import FollicleWidget
from jointWidget import JointWidget
from groupWidget import GroupWidget


class MainWindow(QtWidgets.QMainWindow):

    _BTN_STYLE = ("QPushButton:hover"
                  "{"
                  "background-color:green"
                  "}")

    def __init__(self, parent=None):
        super().__init__()

        # Title
        _title_label = QtWidgets.QLabel("Rig Tools")
        _title_label.setAlignment(QtCore.Qt.AlignCenter)

        # Controller Widget
        _controller_widget = ControllerWidget()

        # Follicle Widget
        _follicle_widget = FollicleWidget()

        # Joint Widget
        _joint_widget = JointWidget()

        # Joint Widget
        _group_widget = GroupWidget()

        # Tab Widget
        _tabs = QtWidgets.QTabWidget()
        _tabs.addTab(_controller_widget, "Controller")
        _tabs.addTab(_follicle_widget, "Follicle")
        _tabs.addTab(_joint_widget, "Joint")
        _tabs.addTab(_group_widget, "Group")

        # Infos
        _infos_label = QtWidgets.QLabel("Emmanuel Chagnon 12/2025")
        _infos_label.setAlignment(QtCore.Qt.AlignCenter)

        # Main Layout
        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(_title_label)
        _layout.addWidget(_tabs)
        _layout.addWidget(_infos_label)

        # Main Widget
        _widget = QtWidgets.QWidget()
        _widget.setLayout(_layout)
        self.setCentralWidget(_widget)

        # Settings
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.setStyleSheet(self._BTN_STYLE)


def run():
    try:
        in_maya = not cmds.about(batch=True)
    except:
        in_maya = False

    try:
        import qdarktheme
        qdarktheme.setup_theme()
    except ImportError:
        print("Dark Theme was not found")

    if in_maya:
        window = MainWindow()
        window.show()

    else:
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        app.exec_()


if __name__ == '__main__':
    run()