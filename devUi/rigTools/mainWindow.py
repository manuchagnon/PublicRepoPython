import sys
from Qt import QtWidgets, QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from devUi.customWidgets.api import HeaderWidget
from devUi.utils.api import get_color

from .controllerWidget import ControllerWidget
from .follicleWidget import FollicleWidget
from .jointWidget import JointWidget
from .groupWidget import GroupWidget
from .nameWidget import NameWidget
from devUi.skinTools.mainWindow import SkinWindow


class RigWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    TOOL_NAME = "RigWindow"

    STYLE_SHEET = (
        """
        QPushButton:hover {
        background-color:green
        }
        """
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        # Follicle
        follicle_widget = FollicleWidget()

        # Controller
        controller_widget = ControllerWidget()

        # Joint
        joint_widget = JointWidget()

        # Joint
        group_widget = GroupWidget()

        # Skinning
        skinning_widget = SkinWindow()

        # Rename
        rename_widget = NameWidget()

        # Tab Widget
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(controller_widget, "Controller")
        tabs.addTab(follicle_widget, "Follicle")
        tabs.addTab(joint_widget, "Joint")
        tabs.addTab(rename_widget, "Name")
        tabs.addTab(group_widget, "Group")
        tabs.addTab(skinning_widget, "Skinning")

        # Infos
        _infos_label = QtWidgets.QLabel("Emmanuel Chagnon 03/2026\nchagnon.emmanuel@gmail.com")
        _infos_label.setAlignment(QtCore.Qt.AlignCenter)

        # Main Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(HeaderWidget(title = "Rig Tools", color = get_color("lila")))
        layout.addWidget(tabs)
        layout.addWidget(_infos_label)

        # Settings
        self.setLayout(layout)
        self.setWindowTitle(self.TOOL_NAME)
        self.setMinimumWidth(425)
        self.setMinimumHeight(700)
        self.setStyleSheet(self.STYLE_SHEET)

if __name__ == '__main__':
    wid = RigWindow()
    wid.show()
