import sys
from PySide6 import QtWidgets, QtCore, QtGui

from devUi.utils.api import *
from devMaya.utils.api import create_jnt

from maya import cmds

class JointWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Suffix
        self._line_suffix = QtWidgets.QLineEdit()
        self._line_suffix.setPlaceholderText("None")

        # Button
        button = QtWidgets.QPushButton("Create Joints under selection")
        button.clicked.connect(self._create_joint_on_selection)
        button.setFixedHeight(50)

        # Layout
        _layout = QtWidgets.QFormLayout()
        _layout.setLabelAlignment(QtCore.Qt.AlignRight)

        _layout.addRow("Suffix :", self._line_suffix)
        _layout.addRow(button)

        self.setLayout(_layout)


    def _create_joint_on_selection(self):
        """
        Call the custom maya function to create the joints under selection
        """
        print(">> Creating Joint under Selection")

        create_jnt()


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
        joint_widget = JointWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(joint_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

    else:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")

        joint_widget = JointWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(joint_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

        app.exec_()
