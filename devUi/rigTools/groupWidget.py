import sys
from PySide6 import QtWidgets, QtCore, QtGui

from devUi.utils.api import *

from devMaya.utils.api import create_grp

from maya import cmds

class GroupWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Separator
        _separator = Separator()

        # Suffix
        self._line_suffix = QtWidgets.QLineEdit()
        self._line_suffix.setPlaceholderText("+ '_grp'")

        # Gizmo Setting
        self._combobox_gizmo = QtWidgets.QComboBox()
        self._combobox_gizmo.addItems(["normal", "at world origin", "at object"])
        self._combobox_gizmo.currentIndexChanged.connect(self.refresh)

        _button_create_grp = QtWidgets.QPushButton("Create group on selection")
        _button_create_grp.clicked.connect(self._create_grp)

        # Gizmo Object Name
        self._line_object = QtWidgets.QLineEdit()
        self._line_object.setPlaceholderText("None")
        self._line_object.setDisabled(True)

        # Create controller Layout
        _layout = QtWidgets.QFormLayout()
        _layout.addWidget(_separator)
        _layout.setLabelAlignment(QtCore.Qt.AlignRight)
        _layout.addRow("Group suffix :", self._line_suffix)
        _layout.addWidget(_separator)
        _layout.addRow("Group gizmo :", self._combobox_gizmo)
        _layout.addRow("Gizmo Target Object :", self._line_object)
        _layout.addWidget(_separator)
        _layout.addRow(_button_create_grp)

        self.setLayout(_layout)

    def refresh(self):
        if self._combobox_gizmo.currentText() == "at object":
            self._line_object.setDisabled(False)
        else:
            self._line_object.setDisabled(True)

    def _create_grp(self):
        gizmo_setting = self._combobox_gizmo.currentText()
        print(">> Create Group with gizmo", gizmo_setting)

        gizmo_target_obj = None

        if gizmo_setting == "normal":
            gizmo = 0
        elif gizmo_setting == "at world origin":
            gizmo = 1
        elif gizmo_setting == "at object":
            gizmo = 2
            gizmo_target_obj = self._line_object.text()

        suffix = self._line_suffix.text()

        create_grp(obj_list=None, guizmo=gizmo, guizmo_target_obj=gizmo_target_obj, suffix = suffix)



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
        group_widget = GroupWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(group_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

    else:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")

        group_widget = GroupWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(group_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

        app.exec_()

if __name__ == '__main__':
    run()
