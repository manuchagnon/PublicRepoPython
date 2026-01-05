import sys
from PySide6 import QtWidgets, QtCore, QtGui

from devUi.utils.api import *

from maya import cmds

class ControllerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Separator
        _separator = Separator()

        # Create Controller
        self._combobox_parent = QtWidgets.QComboBox()
        self._combobox_parent.addItems(["no parenting", "child", "parent"])

        self._box_add_jnt = QtWidgets.QCheckBox("Add joint inside controller")

        _button_create_ctl = QtWidgets.QPushButton("Create Circle Controller on Selection")
        _button_create_ctl.clicked.connect(self._create_ctl)

        # Create controller Layout
        _create_layout = QtWidgets.QFormLayout()
        _create_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        _create_layout.addRow("Choose a parenting option :", self._combobox_parent)
        _create_layout.addRow(self._box_add_jnt)
        _create_layout.addRow(_button_create_ctl)

        _group_create = QtWidgets.QGroupBox("Create")
        _group_create.setLayout(_create_layout)


        # Scale Controller
        # -- Shortcut
        _shortcut_layout = QtWidgets.QHBoxLayout()
        for i in [0.2, 0.5, 0.8, 1.2, 1.5, 2]:
            btn = QtWidgets.QPushButton(str(i))
            btn.clicked.connect(lambda checked, k=i: self._set_ctl_scale(k))
            _shortcut_layout.addWidget(btn)

        # -- Custom Scale
        _line_scale_label = QtWidgets.QLabel("Set Controller Scale to")
        self._line_scale = QtWidgets.QLineEdit()
        self._line_scale.setPlaceholderText("1")

        _button_scale_ctl = QtWidgets.QPushButton("Set Controller Scale ")
        _button_scale_ctl.clicked.connect(self._set_ctl_custom_scale)

        _custom_scale_layout = QtWidgets.QHBoxLayout()
        _custom_scale_layout.addWidget(_line_scale_label)
        _custom_scale_layout.addWidget(self._line_scale)
        _custom_scale_layout.addWidget(_button_scale_ctl)

        # Scale Controller Layout
        _scale_layout = QtWidgets.QVBoxLayout()
        _scale_layout.addLayout(_shortcut_layout)
        _scale_layout.addLayout(_custom_scale_layout)

        _group_scale = QtWidgets.QGroupBox("Scale")
        _group_scale.setLayout(_scale_layout)


        # Pivot Controller Layout
        _pivot_layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("On")
        _pivot_layout.addWidget(label)

        for axis in ["X", "Y", "Z"]:
            btn = QtWidgets.QPushButton(axis)
            btn.clicked.connect(lambda checked, k=axis: self._rotate_ctl(k))

            # btn.clicked.connect(lambda k=axis: self._rotate_ctl(k))
            _pivot_layout.addWidget(btn)

        label = QtWidgets.QLabel("by")
        _pivot_layout.addWidget(label)

        self._line_degrees = QtWidgets.QLineEdit()
        self._line_degrees.setPlaceholderText("90")
        _pivot_layout.addWidget(self._line_degrees)

        label = QtWidgets.QLabel("degrees")
        _pivot_layout.addWidget(label)

        _group_pivot = QtWidgets.QGroupBox("Rotate")
        _group_pivot.setLayout(_pivot_layout)

        # Main Layout
        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(_separator)
        _layout.addWidget(_group_create)
        _layout.addWidget(_separator)
        _layout.addWidget(_group_scale)
        _layout.addWidget(_separator)
        _layout.addWidget(_group_pivot)


        self.setLayout(_layout)

    def _create_ctl(self):
        print(">> Creating Controllers")


    def _set_ctl_custom_scale(self):
        value = self._line_scale.text()
        try:
            value = float(value)
        except:
            if value == "":
                value = 1.0
            else:
                print(value, "is not accpeted, should be int or float")
                return

        self._set_ctl_scale(value)

    def _set_ctl_scale(self, value):
        print(">> Setting Controller Scale to", value)

    def _rotate_ctl(self, axis):
        degrees = self._line_degrees.text()
        try:
            degrees = int(degrees)
        except:
            if degrees == "":
                degrees = 90
            else:
                print(degrees, "is not accpeted, should be int")
                return

        print(">> Rotating Controller on", axis, "by", degrees, "degrees")

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
        ctl_widget = ControllerWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ctl_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

    else:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")

        ctl_widget = ControllerWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ctl_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.show()

        app.exec_()


if __name__ == '__main__':
    run()