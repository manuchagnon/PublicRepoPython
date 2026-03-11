import sys
from Qt import QtWidgets, QtCore, QtGui

from devUi.utils.api import *
from devUi.customWidgets.api import HeaderWidget, Separator

from devMaya.utils.api import create_grps

from maya import cmds

class GroupWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Suffix
        self._line_suffix = QtWidgets.QLineEdit()
        self._line_suffix.setPlaceholderText("+ '_grp'")

        # Gizmo Setting
        self._combobox_gizmo = QtWidgets.QComboBox()
        self._combobox_gizmo.addItems(["normal", "at world origin", "at object"])
        self._combobox_gizmo.currentIndexChanged.connect(self.refresh)

        _button_create_grp = QtWidgets.QPushButton("Create group on selection")
        _button_create_grp.setFixedHeight(50)
        _button_create_grp.clicked.connect(self._create_grp)

        # Gizmo Object Name
        self._line_object = QtWidgets.QLineEdit()
        self._line_object.setPlaceholderText("None")
        self._line_object.setDisabled(True)

        # Form Layout
        layout = QtWidgets.QFormLayout()
        layout.addWidget(Separator())
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.addRow("Group suffix :", self._line_suffix)
        layout.addWidget(Separator())
        layout.addRow("Group gizmo :", self._combobox_gizmo)
        layout.addRow("Gizmo Target Object :", self._line_object)
        layout.addWidget(Separator())
        layout.addRow(_button_create_grp)

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(HeaderWidget(title = "Group", color = get_color("red")))
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

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
        else:
            gizmo=0

        suffix = self._line_suffix.text()

        create_grps(obj_list=[], gizmo_status=gizmo, gizmo_target_obj=gizmo_target_obj, suffix = suffix, in_autorig=False)