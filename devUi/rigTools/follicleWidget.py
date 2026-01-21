import sys
from PySide6 import QtWidgets, QtCore, QtGui

from devMaya.utils.api import create_flc_on_surface, create_FK_ctl, create_jnt, create_set
from devUi.utils.api import *

from maya import cmds

class FollicleWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        
        # Surface
        self._line_srf = QtWidgets.QLineEdit()
        self._line_srf.setPlaceholderText("surface name")
        
        # U
        self._line_flc_on_u = QtWidgets.QLineEdit()
        self._line_flc_on_u.setPlaceholderText("1")

        self._line_param_u_start = QtWidgets.QLineEdit()
        self._line_param_u_start.setPlaceholderText("0.0")

        
        self._line_param_u_end = QtWidgets.QLineEdit()
        self._line_param_u_end.setPlaceholderText("1.0")


        self._line_param_u_offset = QtWidgets.QLineEdit()
        self._line_param_u_offset.setPlaceholderText("0.0")


        # V
        self._line_flc_on_v = QtWidgets.QLineEdit()
        self._line_flc_on_v.setPlaceholderText("1")


        self._line_param_v_start = QtWidgets.QLineEdit()
        self._line_param_v_start.setPlaceholderText("0.0")


        self._line_param_v_end = QtWidgets.QLineEdit()
        self._line_param_v_end.setPlaceholderText("1.0")


        self._line_param_v_offset = QtWidgets.QLineEdit()
        self._line_param_v_offset.setPlaceholderText("0.0")


        # Parameters
        self._box_switch = QtWidgets.QCheckBox("Switch your u and v settings")
        self._box_add_controller = QtWidgets.QCheckBox("Add controllers inside follicle")
        self._box_add_joint = QtWidgets.QCheckBox("Add joints inside follicle")
        self._box_add_set = QtWidgets.QCheckBox("Add new selection set with follicles inside")
        self._box_add_set.setChecked(True)

        # Button
        button = QtWidgets.QPushButton("Create Follicle on Surface")
        button.clicked.connect(self._create_follicle_on_surface)
        button.setFixedHeight(50)

        # Separator
        _separator = Separator()

        # Form Layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.addRow("On selected surface or on", self._line_srf)
        layout.addRow("How many follicle on U ?", self._line_flc_on_u)
        layout.addRow("Starting at", self._line_param_u_start)
        layout.addRow("Ending at", self._line_param_u_end)
        layout.addRow("With an offset of", self._line_param_u_offset)

        layout.addRow(_separator)

        layout.addRow("How many follicle on V ?", self._line_flc_on_v)
        layout.addRow("Starting at", self._line_param_v_start)
        layout.addRow("Ending at", self._line_param_v_end)
        layout.addRow("With an offset of", self._line_param_v_offset)

        layout.addRow(_separator)

        layout.addRow(self._box_switch)
        layout.addRow(self._box_add_controller)
        layout.addRow(self._box_add_joint)
        layout.addRow(self._box_add_set)

        layout.addRow(_separator)

        layout.addRow(button)

        self.setLayout(layout)

    def _create_follicle_on_surface(self):
        """
        Call the custom maya function to create the follicle on surface with custom parameters from ui
        """
        print(">> Creating Follicle on Surface")

        surface = self._line_srf.text() or None

        flc_on_u = int(self._line_flc_on_u.text()) or 1
        u_start = float(self._line_param_u_start.text()) or 0.0
        u_end = float(self._line_param_u_end.text()) or 1.0
        u_offset = float(self._line_param_u_offset.text()) or 0.0

        flc_on_v = int(self._line_flc_on_v.text()) or 1
        v_start = float(self._line_param_v_start.text()) or 0.0
        v_end = float(self._line_param_v_end.text()) or 1.0
        v_offset = float(self._line_param_v_offset.text()) or 0.0

        switch = self._box_switch.isChecked()
        add_ctl = self._box_add_controller.isChecked()
        add_jnt = self._box_add_joint.isChecked()
        add_set = self._box_add_set.isChecked()

        if switch: # switch U and V parameters
            switch_flc_on_u = flc_on_u
            switch_u_start = u_start
            switch_u_end = u_end
            switch_u_offset = u_offset

            flc_on_u = flc_on_v
            u_start = v_start
            u_end = v_end
            u_offset = v_offset

            flc_on_v = switch_flc_on_u
            v_start = switch_u_start
            v_end = switch_u_end
            v_offset = switch_u_offset

        flc_created = create_flc_on_surface(
            surface,
            flc_on_u,
            flc_on_v,

            flc_param_u_start = u_start,
            flc_param_u_end = u_end,
            flc_param_u_offset = u_offset,

            flc_param_v_start = v_start,
            flc_param_v_end = v_end,
            flc_param_v_offset = v_offset
        )

        if add_ctl:
            ctl_created, ctl_grp_created = create_FK_ctl(flc_created, parent = 1)
            if add_jnt:
                jnt_created = create_jnt(ctl_created, parent=1)

        if add_jnt and not add_ctl:
            jnt_created = create_jnt(flc_created, parent = 1)

        if add_set:
            create_set(flc_created)


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
        follicle_widget = FollicleWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(follicle_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

    else:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")

        follicle_widget = FollicleWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(follicle_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

        app.exec_()

if __name__ == '__main__':
    run()