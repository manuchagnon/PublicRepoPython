from Qt import QtWidgets, QtCore, QtGui
from maya import cmds

from devUi.utils.api import get_color, color_dict
from devUi.customWidgets.api import HeaderWidget, TreeWidget

from devMaya.utils.api import (create_ctls, scale_ctls, rotate_ctls, create_jnts, color_ctls,
                               ctl_custom_shapes, change_ctl_shapes, change_ctl_shapes_by_ctl_source, select_all_cvs,
                               change_ctl_shapes_by_shape_name, change_ctl_line_widths,
                               undo_chunk
                               )

class ControllerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Main Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(HeaderWidget(title = "Controller", color = get_color("green")))
        layout.addSpacing(5)
        layout.addWidget(self._build_create_group())
        layout.addSpacing(5)
        layout.addLayout(self._build_scale_layout())
        layout.addSpacing(5)
        layout.addWidget(self._build_color_group())
        layout.addSpacing(5)
        layout.addWidget(self._build_shape_group())

        self.setLayout(layout)

        self.refresh()
    # UI
    def _build_create_group(self) -> QtWidgets.QGroupBox:
        # Create Controller
        self._combobox_parent = QtWidgets.QComboBox()
        self._combobox_parent.addItems(["no parenting", "child", "parent"])

        self._box_add_jnt = QtWidgets.QCheckBox("Add joint inside controller")

        button_create_ctl = QtWidgets.QPushButton("Create Circle Controller on Selection")
        button_create_ctl.clicked.connect(self._create_ctl)

        # Create controller Layout
        create_layout = QtWidgets.QFormLayout()
        create_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        create_layout.addRow("Choose a parenting option :", self._combobox_parent)
        create_layout.addRow(self._box_add_jnt)
        create_layout.addRow(button_create_ctl)

        group_create = QtWidgets.QGroupBox("Create")
        group_create.setLayout(create_layout)

        return group_create

    def _build_scale_layout(self) -> QtWidgets.QHBoxLayout:
        # Scale Controller
        # -- Shortcut
        shortcut_layout = QtWidgets.QHBoxLayout()
        for i in [-1, 0.2, 0.5, 0.8, 1.2, 1.5, 2]:
            btn = QtWidgets.QPushButton(str(i))
            btn.clicked.connect(lambda checked=None, k=i: self._set_ctl_scale(k))
            shortcut_layout.addWidget(btn)

        # -- Custom Scale
        line_scale_label = QtWidgets.QLabel("Set Controller Scale to")
        self._line_scale = QtWidgets.QLineEdit()
        self._line_scale.setPlaceholderText("1")

        button_scale_ctl = QtWidgets.QPushButton("Set Scale ")
        button_scale_ctl.clicked.connect(self._set_ctl_custom_scale)

        custom_scale_layout = QtWidgets.QHBoxLayout()
        custom_scale_layout.addWidget(line_scale_label)
        custom_scale_layout.addWidget(self._line_scale)
        custom_scale_layout.addWidget(button_scale_ctl)

        # Scale Controller Group
        scale_layout = QtWidgets.QVBoxLayout()
        scale_layout.addLayout(shortcut_layout)
        scale_layout.addLayout(custom_scale_layout)

        group_scale = QtWidgets.QGroupBox("Scale")
        group_scale.setLayout(scale_layout)

        # Rotate Controller Group
        rotate_layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("On")
        rotate_layout.addWidget(label)

        for axis in ["X", "Y", "Z"]:
            btn = QtWidgets.QPushButton(axis)
            btn.clicked.connect(lambda checked=None, k=axis: self._rotate_ctl(k))
            rotate_layout.addWidget(btn)

        label = QtWidgets.QLabel("by")
        rotate_layout.addWidget(label)

        self._line_degrees = QtWidgets.QLineEdit()
        self._line_degrees.setPlaceholderText("90")
        rotate_layout.addWidget(self._line_degrees)

        label = QtWidgets.QLabel("degrees")
        rotate_layout.addWidget(label)

        group_rotate = QtWidgets.QGroupBox("Rotate")
        group_rotate.setLayout(rotate_layout)

        # Scale Rotate Layout
        scale_rotate_layout = QtWidgets.QHBoxLayout()
        scale_rotate_layout.addWidget(group_scale)
        scale_rotate_layout.addWidget(group_rotate)

        return scale_rotate_layout

    def _build_color_group(self) -> QtWidgets.QGroupBox :
        # Color Group
        color_cube_layout = QtWidgets.QGridLayout()
        color_cube_layout.setSpacing(3)
        colors_by_row = 12
        row = 0
        column = 0
        for i, (color_name, color) in enumerate(color_dict().items()):
            btn = QtWidgets.QPushButton()
            btn.clicked.connect(lambda checked=None, c=color: self._color_ctl(c))
            color = [str(c) for c in color]
            btn.setStyleSheet("background-color: rgb(" + ",".join(color) + ");")
            btn.setToolTip(color_name)
            column = i % colors_by_row
            row = i // colors_by_row
            color_cube_layout.addWidget(btn, row, column)

        group_color = QtWidgets.QGroupBox("Color")
        group_color.setLayout(color_cube_layout)

        return group_color

    def _build_shape_group(self) -> QtWidgets.QGroupBox :
        # Shape Group

        self.shape_tree = TreeWidget()
        self.shape_tree.set_placeholder_text("No Custom Shape")
        self.shape_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.shape_tree.setHeaderLabels(["Custom Shapes"])

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.shape_tree)

        btn_change_shape_custom = QtWidgets.QPushButton("Apply custom shape")
        btn_change_shape_custom.clicked.connect(self._change_ctl_shape_custom)
        btn_change_shape_by_selection = QtWidgets.QPushButton("Apply last selected shape")
        btn_change_shape_by_selection.clicked.connect(self._change_ctl_shape_selected)
        btn_select_cv = QtWidgets.QPushButton("Select all CVs")
        btn_select_cv.clicked.connect(self._select_all_cv)

        center_layout = QtWidgets.QVBoxLayout()
        center_layout.addWidget(btn_change_shape_custom)
        center_layout.addWidget(btn_change_shape_by_selection)
        center_layout.addWidget(btn_select_cv)

        lay = QtWidgets.QHBoxLayout()
        for i in [1, 2, 4, 8, 12]:
            btn = QtWidgets.QPushButton(str(i))
            btn.clicked.connect(lambda checked=None, k=i: self._set_ctl_line_width(k))
            lay.addWidget(btn)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(QtWidgets.QLabel("Set shape line width"))
        right_layout.addLayout(lay)
        right_layout.addStretch()


        shape_layout = QtWidgets.QHBoxLayout()
        shape_layout.addLayout(left_layout)
        shape_layout.addLayout(center_layout)
        shape_layout.addLayout(right_layout)

        shape_group = QtWidgets.QGroupBox("Shape")
        shape_group.setLayout(shape_layout)

        return shape_group

    def refresh(self):

        # fill shape tree
        for shape, shape_data in ctl_custom_shapes().items():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, shape)

            item.setData(0, QtCore.Qt.UserRole, (shape_data["cv_pos"], shape_data["degree"], shape_data["periodic"]))

            self.shape_tree.addTopLevelItem(item)

    # Functions
    @undo_chunk
    def _create_ctl(self):
        print(">> Creating Controllers")

        if self._combobox_parent.currentText() == "no parenting":
            parent=0
        elif self._combobox_parent.currentText() == "child":
            parent = 1
        elif self._combobox_parent.currentText() == "parent":
            parent = 2
        else:
            parent = 0

        ctl_list = create_ctls(obj_list=[], parent=parent, in_autorig=False)

        if self._box_add_jnt.isChecked():
            create_jnts(ctl_list, in_autorig=False)


    def _set_ctl_custom_scale(self):
        value = self._line_scale.text()
        scale = float(value) if value != "" else 1.0
        self._set_ctl_scale(scale)

    @undo_chunk
    def _set_ctl_scale(self, value : float):
        print(">> Setting Controller Scale to", value)
        scale_ctls(ctl_list = [], scale = value, in_autorig=False)

    @undo_chunk
    def _rotate_ctl(self, axis):
        value = self._line_degrees.text()

        degrees = int(value) if value != "" else 90

        # print(degrees, "is not accepted, should be int")

        print(">> Rotating Controller on", axis, "axis by", degrees, "degrees")

        rotate_ctls(ctl_list = [], axis = axis, degrees = degrees, in_autorig=False)

    @undo_chunk
    def _color_ctl(self, color):
        print(">> Change Controller color to", color)
        color_ctls(ctl_list = [], color = color, in_autorig=False)


    @undo_chunk
    def _change_ctl_shape_custom(self):
        shape_item = self.shape_tree.selectedItems()[0]

        cv_pos, degree, periodic = shape_item.data(0, QtCore.Qt.UserRole)

        change_ctl_shapes_by_shape_name(ctl_list = [], shape_name = shape_item.text(0), in_autorig=False)

        # change_ctl_shapes(ctl_list=[], cv=cv_pos, degree=degree, periodic=periodic, in_autorig=False)

        print(">> Change Controller shape to", shape_item.text(0))

    @undo_chunk
    def _change_ctl_shape_selected(self):

        change_ctl_shapes_by_ctl_source(ctl_list=[], ctl_source=None)

        print(">> Change Controller shape to last selected Controller shape")

    @undo_chunk
    def _set_ctl_line_width(self, width):

        change_ctl_line_widths(ctl_list=[], width=width, in_autorig=False)

        print(">> Change Controller shape line width to", width)


    @undo_chunk
    def _select_all_cv(self):

        select_all_cvs(ctl_list=[])

        print(">> Select all selected controllers CVs")
