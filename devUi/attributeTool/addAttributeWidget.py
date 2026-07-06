
import maya.cmds as cmds
# from PySide6 import QtCore, QtWidgets
from Qt import QtCore, QtWidgets

from maya import cmds

from devMaya.utils.attribute import Attribute

ATTR_TYPES = [
    "Vector", "Float", "Integer", "Boolean", "String", "Enum",
    "Matrix", "Message", "Double", "Long", "Short", "Byte",
    "Char", "Float2", "Float3", "Double2", "Double3",
    "Long2", "Long3", "Short2", "Short3",
]

DATA_TYPES = ["Float", "String", "Matrix", "Integer", "Boolean", "Vector"]

NUMERIC_TYPES = {
    "Float", "Integer", "Double", "Long", "Short", "Byte", "Char",
    "Float2", "Float3", "Double2", "Double3",
    "Long2", "Long3", "Short2", "Short3", "Vector",
}

# Maya addAttr keyword per type
ATTR_TYPE_MAP = {
    "Vector":   dict(at="double3"),
    "Float":    dict(at="float"),
    "Integer":  dict(at="long"),
    "Boolean":  dict(at="bool"),
    "String":   dict(dt="string"),
    "Enum":     dict(at="enum"),
    "Matrix":   dict(at="matrix"),
    "Message":  dict(at="message"),
    "Double":   dict(at="double"),
    "Long":     dict(at="long"),
    "Short":    dict(at="short"),
    "Byte":     dict(at="byte"),
    "Char":     dict(at="char"),
    "Float2":   dict(at="float2"),
    "Float3":   dict(at="float3"),
    "Double2":  dict(at="double2"),
    "Double3":  dict(at="double3"),
    "Long2":    dict(at="long2"),
    "Long3":    dict(at="long3"),
    "Short2":   dict(at="short2"),
    "Short3":   dict(at="short3"),
}

class AddAttributeWidget(QtWidgets.QWidget):

    add_clicked = QtCore.Signal(Attribute)
    remove_clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._build_ui()
        self._connect_signals()
        self._refresh_type_ui("Float")

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # # ── Node / Object field ──────────────────────────────────────
        # node_group = QtWidgets.QGroupBox("Object")
        # node_form  = QtWidgets.QFormLayout(node_group)
        # self.node_label = QtWidgets.QLabel("(no selection)")
        # self.node_label.setStyleSheet("font-style: italic; color: #888;")
        # node_form.addRow("Selected:", self.node_label)
        # main_layout.addWidget(node_group)

        # ── Attribute type section ───────────────────────────────────
        type_group = QtWidgets.QGroupBox("Attribute Type")
        type_layout = QtWidgets.QVBoxLayout(type_group)

        # Radio: Data / Array Data
        radio_row = QtWidgets.QHBoxLayout()
        self.rb_attr  = QtWidgets.QRadioButton("Attribute Type")
        self.rb_data  = QtWidgets.QRadioButton("Data Type")
        self.rb_attr.setChecked(True)
        radio_row.addWidget(self.rb_attr)
        radio_row.addWidget(self.rb_data)
        radio_row.addStretch()
        type_layout.addLayout(radio_row)

        # Combo
        combo_row = QtWidgets.QHBoxLayout()
        combo_row.addWidget(QtWidgets.QLabel("Type:"))
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(ATTR_TYPES)
        self.type_combo.setCurrentText("Float")
        combo_row.addWidget(self.type_combo, 1)
        type_layout.addLayout(combo_row)

        main_layout.addWidget(type_group)

        # ── Naming ──────────────────────────────────────────────────
        name_group  = QtWidgets.QGroupBox("Attribute Naming")
        name_form   = QtWidgets.QFormLayout(name_group)

        self.long_name  = QtWidgets.QLineEdit()
        self.short_name = QtWidgets.QLineEdit()
        self.nice_name  = QtWidgets.QLineEdit()
        self.cb_default_nice = QtWidgets.QCheckBox("Use long name as nice name")
        self.cb_default_nice.setChecked(True)

        name_form.addRow("Long name:",  self.long_name)
        name_form.addRow("Short name:", self.short_name)
        name_form.addRow("Nice name:",  self.nice_name)
        name_form.addRow("",            self.cb_default_nice)

        main_layout.addWidget(name_group)

        # ── Flags ────────────────────────────────────────────────────
        flags_group  = QtWidgets.QGroupBox("Flags")
        flags_layout = QtWidgets.QHBoxLayout(flags_group)
        self.cb_keyable  = QtWidgets.QCheckBox("Keyable")
        self.cb_readable = QtWidgets.QCheckBox("Readable")
        self.cb_writable = QtWidgets.QCheckBox("Writable")
        self.cb_hidden   = QtWidgets.QCheckBox("Hidden")
        self.cb_keyable.setChecked(True)
        self.cb_readable.setChecked(True)
        self.cb_writable.setChecked(True)
        for cb in (self.cb_keyable, self.cb_readable, self.cb_writable, self.cb_hidden):
            flags_layout.addWidget(cb)
        flags_layout.addStretch()
        main_layout.addWidget(flags_group)

        # ── Numeric properties (min/max/default) ────────────────────
        self.numeric_group = QtWidgets.QGroupBox("Numeric Properties")
        num_form = QtWidgets.QFormLayout(self.numeric_group)

        self.cb_min = QtWidgets.QCheckBox("Minimum")
        self.le_min = QtWidgets.QLineEdit("0")
        self.cb_max = QtWidgets.QCheckBox("Maximum")
        self.le_max = QtWidgets.QLineEdit("10")
        self.le_default = QtWidgets.QLineEdit("0")

        min_row = QtWidgets.QHBoxLayout()
        min_row.addWidget(self.cb_min)
        min_row.addWidget(self.le_min, 1)

        max_row = QtWidgets.QHBoxLayout()
        max_row.addWidget(self.cb_max)
        max_row.addWidget(self.le_max, 1)

        num_form.addRow("Default:", self.le_default)
        num_form.addRow("", min_row)
        num_form.addRow("", max_row)

        main_layout.addWidget(self.numeric_group)

        # ── Enum properties ──────────────────────────────────────────
        self.enum_group = QtWidgets.QGroupBox("Enum Fields")
        enum_vbox = QtWidgets.QVBoxLayout(self.enum_group)

        self.enum_list = QtWidgets.QListWidget()
        self.enum_list.setMaximumHeight(120)
        enum_btn_row = QtWidgets.QHBoxLayout()
        self.enum_field = QtWidgets.QLineEdit()
        self.enum_field.setPlaceholderText("New enum value…")
        self.btn_add_enum = QtWidgets.QPushButton("Add")
        self.btn_del_enum = QtWidgets.QPushButton("Remove")
        enum_btn_row.addWidget(self.enum_field, 1)
        enum_btn_row.addWidget(self.btn_add_enum)
        enum_btn_row.addWidget(self.btn_del_enum)
        enum_vbox.addWidget(self.enum_list)
        enum_vbox.addLayout(enum_btn_row)

        main_layout.addWidget(self.enum_group)

        # ── String default ───────────────────────────────────────────
        self.string_group = QtWidgets.QGroupBox("String Default")
        str_form = QtWidgets.QFormLayout(self.string_group)
        self.le_string_default = QtWidgets.QLineEdit()
        str_form.addRow("Default value:", self.le_string_default)
        main_layout.addWidget(self.string_group)

        # ── Parent attribute (for compound children) ─────────────────
        self.parent_group = QtWidgets.QGroupBox("Parent Attribute (optional)")
        parent_form = QtWidgets.QFormLayout(self.parent_group)
        # self.le_parent = QtWidgets.QLineEdit()
        # self.le_parent.setPlaceholderText("e.g. myCompound")
        # parent_form.addRow("Parent attr:", self.le_parent)
        main_layout.addWidget(self.parent_group)

        # ── Buttons ───────────────────────────────────────────────────
        btn_layout = QtWidgets.QHBoxLayout()
        # self.btn_ok = QtWidgets.QPushButton("OK")
        self.btn_add = QtWidgets.QPushButton("Add New Attribute")
        # self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_remove = QtWidgets.QPushButton("Remove Selected Attribute")

        # self.btn_ok.setDefault(True)
        btn_layout.addStretch()
        # btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        # btn_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(btn_layout)

    def _connect_signals(self):
        self.type_combo.currentTextChanged.connect(self._refresh_type_ui)
        self.rb_attr.toggled.connect(self._on_radio_toggle)
        self.rb_data.toggled.connect(self._on_radio_toggle)

        self.cb_min.toggled.connect(self.le_min.setEnabled)
        self.cb_max.toggled.connect(self.le_max.setEnabled)

        self.long_name.textChanged.connect(self._on_long_name_changed)
        self.cb_default_nice.toggled.connect(self._on_default_nice_toggled)

        self.btn_add_enum.clicked.connect(self._add_enum_item)
        self.btn_del_enum.clicked.connect(self._remove_enum_item)

        # self.btn_ok.clicked.connect(self._on_ok)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_remove.clicked.connect(self.remove_clicked.emit)
        # self.btn_cancel.clicked.connect(self.close)

        # Update node label whenever dialog gets focus
        # self.installEventFilter(self)

    def _on_radio_toggle(self):
        if self.rb_attr.isChecked():
            self.type_combo.clear()
            self.type_combo.addItems(ATTR_TYPES)
        else:
            self.type_combo.clear()
            self.type_combo.addItems(DATA_TYPES)
        self.type_combo.setCurrentIndex(0)

    def _refresh_type_ui(self, attr_type):
        is_numeric = attr_type in NUMERIC_TYPES
        is_enum    = attr_type == "Enum"
        is_string  = attr_type == "String"

        self.numeric_group.setVisible(is_numeric)
        self.enum_group.setVisible(is_enum)
        self.string_group.setVisible(is_string)

        # Min/max respect their checkboxes
        self.le_min.setEnabled(self.cb_min.isChecked())
        self.le_max.setEnabled(self.cb_max.isChecked())

    def _on_long_name_changed(self, text):
        if self.cb_default_nice.isChecked():
            nice = text.replace("_", " ").strip()
            # Insert space before capitals (camelCase → Camel Case)
            import re
            nice = re.sub(r'([a-z])([A-Z])', r'\1 \2', nice)
            self.nice_name.setText(nice)

    def _on_default_nice_toggled(self, checked):
        self.nice_name.setReadOnly(checked)
        if checked:
            self._on_long_name_changed(self.long_name.text())

    def _add_enum_item(self):
        val = self.enum_field.text().strip()
        if val:
            self.enum_list.addItem(val)
            self.enum_field.clear()

    def _remove_enum_item(self):
        for item in self.enum_list.selectedItems():
            self.enum_list.takeItem(self.enum_list.row(item))

    def _validate(self):
        long_name = self.long_name.text().strip()
        if not long_name:
            QtWidgets.QMessageBox.warning(self, "Validation", "Long name cannot be empty.")
            return False

        # Must start with a letter
        from re import match
        if not match(r'^[A-Za-z]', long_name):
            QtWidgets.QMessageBox.warning(
                self, "Validation",
                "Attribute name must begin with a letter (a-z / A-Z).")
            return False

        # Check no selection
        # if not cmds.ls(sl=True):
        #     QtWidgets.QMessageBox.warning(
        #         self, "Validation",
        #         "Nothing selected. Please select a node first.")
        #     return False

        return True

    def _collect_kwargs(self):
        """
        Create a new Attribute object to fill the Ui
        """
        attr_type  = self.type_combo.currentText()
        long_name  = self.long_name.text().strip()
        short_name = self.short_name.text().strip()
        nice_name  = self.nice_name.text().strip()

        kwargs = dict(long_name=long_name)
        my_type = ATTR_TYPE_MAP.get(attr_type, dict(at="float"))
        kwargs.update(my_type)

        if short_name:
            kwargs["shortName"] = short_name
        if nice_name and not self.cb_default_nice.isChecked():
            kwargs["nice_name"] = nice_name
        elif self.cb_default_nice.isChecked():
            kwargs["nice_name"] = self.nice_name.text()

        # Flags
        kwargs["keyable"] = self.cb_keyable.isChecked()
        kwargs["readable"] = self.cb_readable.isChecked()
        kwargs["writable"] = self.cb_writable.isChecked()
        kwargs["hidden"] = self.cb_hidden.isChecked()

        # Numeric
        if attr_type in NUMERIC_TYPES:
            try:
                kwargs["default_value"] = float(self.le_default.text())
            except ValueError:
                pass
            if self.cb_min.isChecked():
                try:
                    kwargs["minValue"] = float(self.le_min.text())
                except ValueError:
                    pass
            if self.cb_max.isChecked():
                try:
                    kwargs["maxValue"] = float(self.le_max.text())
                except ValueError:
                    pass

        # Enum
        if attr_type == "Enum":
            items = [self.enum_list.item(i).text()
                     for i in range(self.enum_list.count())]
            if items:
                kwargs["enum_names"] = ":".join(items)

        # String default
        if attr_type == "String":
            dv = self.le_string_default.text()
            if dv:
                kwargs["defaultString"] = dv

        # Parent
        # parent = self.le_parent.text().strip()
        # if parent:
        #     kwargs["parent"] = parent

        return kwargs

    # def _apply(self):
    #     if not self._validate():
    #         return False
    #
    #     node  = self._obj
    #     kwargs = self._collect_kwargs()
    #
    #     # create the Attribute()
    #     attr = Attribute(long_name=kwargs["long_name"], attr_dict=kwargs)
    #
    #     self.emit.add_clicked(attr)
        """
        errors = []
        for node in nodes:
            try:
                cmds.addAttr(node, **kwargs)

                # For String type we need to set default via setAttr
                if self.type_combo.currentText() == "String":
                    dv = self.le_string_default.text()
                    if dv:
                        cmds.setAttr(
                            "{}.{}".format(node, kwargs["longName"]),
                            dv, type="string")

            except Exception as e:
                errors.append("{}: {}".format(node, str(e)))

        if errors:
            QtWidgets.QMessageBox.warning(
                self, "Errors",
                "Some attributes could not be added:\n\n" + "\n".join(errors))
            return False
        """
        return True

    def _on_add(self):
        """ Emit the add signal with new Attribute object """

        if not self._validate():
            return False

        kwargs = self._collect_kwargs()

        # create the Attribute()
        attr = Attribute(long_name=kwargs["long_name"],
                         type=kwargs["at"],
                         attr_dict=kwargs)
        self.add_clicked.emit(attr)

