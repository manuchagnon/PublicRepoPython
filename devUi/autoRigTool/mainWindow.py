from Qt import QtWidgets, QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from devUi.customWidgets.api import HeaderWidget
from devUi.utils.api import get_color

class AutoRigWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    TOOL_NAME = "Auto Rig Tools"

    STYLE_SHEET = (
        """
        QPushButton:hover {
        background-color:green
        }
        """
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        # Header
        header = HeaderWidget(title="Auto Rig Tools", color=get_color("lila"))

        # Infos
        infos_label = QtWidgets.QLabel("Emmanuel Chagnon 05/2026\nchagnon.emmanuel@gmail.com")
        infos_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(infos_label)

        # Settings
        self.setLayout(layout)
        self.setWindowTitle(self.TOOL_NAME)
        self.setMinimumWidth(425)
        self.setMinimumHeight(700)
        self.setStyleSheet(self.STYLE_SHEET)