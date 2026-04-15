from Qt import QtWidgets, QtCore, QtGui

from devUi.utils.api import get_color
from devMaya.utils.api import undo_chunk, replace_in_names, add_to_names, rename_and_increment
from devUi.customWidgets.headerWidget import HeaderWidget

class NameWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Search and Replace
        self._target_line = QtWidgets.QLineEdit()
        self._target_line.setPlaceholderText("''")
        self._replace_line = QtWidgets.QLineEdit()
        self._replace_line.setPlaceholderText("''")
        self._target_replace_btn = QtWidgets.QPushButton("Search and Replace")
        self._target_replace_btn.clicked.connect(self._target_replace)

        # Prefix
        self._add_prefix_line = QtWidgets.QLineEdit()
        self._add_prefix_line.setPlaceholderText("''")
        self._add_prefix_btn = QtWidgets.QPushButton("Add Prefix :")
        self._add_prefix_btn.clicked.connect(self._add_prefix)

        # Suffix
        self._add_suffix_line = QtWidgets.QLineEdit()
        self._add_suffix_line.setPlaceholderText("''")
        self._add_suffix_btn = QtWidgets.QPushButton("Add Suffix :")
        self._add_suffix_btn.clicked.connect(self._add_suffix)

        # Rename and Increment
        self._rename_line = QtWidgets.QLineEdit()
        self._rename_line.setPlaceholderText("''")
        self._offset_line = QtWidgets.QLineEdit("0")
        self._offset_line.setPlaceholderText("0")
        self._offset_line.setValidator(QtGui.QIntValidator(0, 99999))
        self._padding_line = QtWidgets.QLineEdit("2")
        self._padding_line.setPlaceholderText("2")
        self._padding_line.setValidator(QtGui.QIntValidator(0, 99999))
        self._rename_increment_btn = QtWidgets.QPushButton("Rename and Increment")
        self._rename_increment_btn.clicked.connect(self._rename_increment)


        # Form Layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.addRow("Search by :", self._target_line)
        layout.addRow("Replace by :", self._replace_line)
        layout.addRow("", self._target_replace_btn)

        layout.addRow("Prefix :", self._add_prefix_line)
        layout.addRow("", self._add_prefix_btn)

        layout.addRow("Prefix :", self._add_suffix_line)
        layout.addRow("", self._add_suffix_btn)

        layout.addRow("Rename :", self._rename_line)
        layout.addRow("Offset Start :", self._offset_line)
        layout.addRow("Padding :", self._padding_line)
        layout.addRow("", self._rename_increment_btn)


        # Main Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(HeaderWidget(title = "Name", color = get_color(5)))
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

    @undo_chunk
    def _target_replace(self):
        target_str = self._target_line.text()
        replace_str = self._replace_line.text()

        print(">> Search for", target_str, "and replace it by", replace_str)

        replace_in_names(name_list=[], target_str=target_str, replace_by_str=replace_str)

    @undo_chunk
    def _add_prefix(self):
        added_str = self._add_prefix_line.text()

        print(">> Add Prefix", added_str)

        add_to_names(name_list=[], added_str=added_str, index=0)

    @undo_chunk
    def _add_suffix(self):
        added_str = self._add_suffix_line.text()

        print(">> Add Suffix", added_str)

        add_to_names(name_list=[], added_str=added_str, index=-1)

    @undo_chunk
    def _rename_increment(self):
        name = self._rename_line.text()
        start = int(self._offset_line.text())
        padding = int(self._padding_line.text())

        print(">> Rename by", name, "and renumber : start at", start,"padding", padding)

        rename_and_increment(name_list=[], base_name=name, start_index=start, padding=padding)

