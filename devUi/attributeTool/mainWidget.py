from PySide6 import QtCore, QtWidgets

from maya import cmds

from devUi.customWidgets.api import HeaderWidget, ListWidget
from devUi.utils.api import *

from devMaya.utils.api import *



class AttributeWidget(QtWidgets.QWidget):

    def __init__(self, short_name, nice_name, type, enum_names=[], locked=False):
        super().__init__()

        # Store attribute parameters
        self.short_name = short_name
        self.nice_name = nice_name
        self.type = type
        self.enum_names = enum_names
        self.locked = locked

class AttributeWindow(QtWidgets.QWidget):

    _BTN_STYLE = ("QPushButton:hover"
                  "{"
                  "background-color:green"
                  "}"
                  )

    def __init__(self, parent=None):
        super().__init__()

        # Header
        _header = HeaderWidget(title = "Attribute Window", color = get_color(2))

        self.obj = None
        self.obj_attr_list = []
        self.separators = []

        # Line Node
        self._line_node = QtWidgets.QLineEdit()
        self._line_node.setPlaceholderText("Transform Node")

        # Label Node
        self._btn_node = QtWidgets.QPushButton("Define Node")
        self._btn_node.clicked.connect(self._define_obj)

        # Node Layout
        node_layout = QtWidgets.QHBoxLayout()
        node_layout.addWidget(self._line_node)
        node_layout.addWidget(self._btn_node)

        # Attribute tree
        self._attr_list = ListWidget()
        self._attr_list.set_placeholder_text("No custom attribute")
        self._attr_list.setBaseSize(50, 100)
        self._attr_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        for i in range(10):
            self._attr_list.addItem('Item {:02d}'.format(i))

        # Button Add Separator
        self._btn_add_separator = QtWidgets.QPushButton("Add Separator")
        self._btn_add_separator.clicked.connect(self._add_separator)

        # Button Remove Separator
        self._btn_remove_separator = QtWidgets.QPushButton("Remove Separator")
        self._btn_remove_separator.clicked.connect(self._remove_separator)

        # Btn Layout
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.addWidget(self._btn_add_separator)
        btn_layout.addWidget(self._btn_remove_separator)

        # Central Horizontal Layout
        attr_layout = QtWidgets.QHBoxLayout()
        attr_layout.addWidget(self._attr_list)
        attr_layout.addLayout(btn_layout)

        # Main Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(node_layout)
        layout.addLayout(attr_layout)
        self.setLayout(layout)

        # Settings
        self.resize(300, 550)
        self.setStyleSheet(self._BTN_STYLE)
        # self._refresh()

    def _add_separator(self):
        """ Adds a custom attribute Separator with a custom name in the list widget """
        pass

    def _remove_separator(self):
        pass

    def _delete_attr(self):
        """ Deletes a custom attribute previously added in the list widget """
        pass

    def _define_obj(self):
        node = select_object(obj=None)

        if node:
            self._line_node.setText(node)
        else:
            print("You must select an object")
    # self._refresh()

