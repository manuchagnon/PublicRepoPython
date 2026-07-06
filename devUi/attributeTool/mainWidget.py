import os
import pickle

# from PySide6 import QtCore, QtWidgets
from Qt import QtCore, QtWidgets

from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from devUi.customWidgets.api import HeaderWidget, ListWidget
from devUi.utils.api import *

from .addAttributeWidget import AddAttributeWidget

from devMaya.utils.api import (
    select_object,

    undo_chunk,

    Attribute,
    Separator,
    lock_attributes,
    connect_attributes,
    add_separator_attribute,
    get_custom_non_hidden_attributes,
    add_custom_attributes,
    create_attribute_cache_node,
    remove_custom_attributes,
    )


base_dir = os.path.dirname(os.path.abspath(__file__))
templates_file_path = os.path.join(base_dir, "attribute_templates.txt")


class AttributeWidget(QtWidgets.QWidget):

    COLORS = [
        str(tuple(Colors()["grey"])),
        str(tuple(Colors()["yellow"])),
        str(tuple(Colors()["sky blue"])),
    ]


    COLOR_BOX_STYLESHEET = "QFrame.ConnexionColorBox {background-color:rgb"f"{COLORS[0]};""}"


    def __init__(self, attribute: Attribute | Separator, parent=None):
        super().__init__(parent=parent)
        self.attribute = attribute

        self._build_layout()

    def _build_layout(self):
        color_box_left = QtWidgets.QFrame()
        color_box_left.setFixedWidth(7)
        color_box_left.setProperty("class", "ConnexionColorBox")
        color_box_right = QtWidgets.QFrame()
        color_box_right.setFixedWidth(7)
        color_box_right.setProperty("class", "ConnexionColorBox")

        if isinstance(self.attribute, Separator):
            color_box_left.setStyleSheet(self.COLOR_BOX_STYLESHEET.replace(self.COLORS[0], self.COLORS[2]))
            color_box_right.setStyleSheet(self.COLOR_BOX_STYLESHEET.replace(self.COLORS[0], self.COLORS[2]))
        else:
            if self.attribute.input_connexion:
                color_box_left.setStyleSheet(self.COLOR_BOX_STYLESHEET.replace(self.COLORS[0], self.COLORS[1]))
            else:
                color_box_left.setStyleSheet(self.COLOR_BOX_STYLESHEET)
            if self.attribute.output_connexions:
                color_box_right.setStyleSheet(self.COLOR_BOX_STYLESHEET.replace(self.COLORS[0], self.COLORS[1]))
            else:
                color_box_right.setStyleSheet(self.COLOR_BOX_STYLESHEET)

        # Label
        label = QtWidgets.QLabel(repr(self.attribute))

        lay = QtWidgets.QHBoxLayout()
        lay.addWidget(color_box_left)
        lay.addWidget(label)
        lay.addStretch()
        lay.addWidget(color_box_right)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)


class AttributeListWidget(ListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._obj = None
        self._attributes : list[Attribute] = []

        self.set_placeholder_text("No custom attribute")
        self.setSpacing(5)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def set_obj(self, obj):
        self._obj = obj

    def set_attributes_from_node(self, attributes: list[str]):
        """
        Fill the list widget with a list of attributes names and the current obj
        """
        self._attributes = []
        self.clear()
        for attr in attributes:
            attr = Attribute(long_name=attr)
            attr = attr.build_attribute_from_node(node=self._obj)
            # print("but from node attr is separator :", isinstance(attr, Separator))
            # print(attr)

            widget = AttributeWidget(attr, parent=self)
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, widget)

            self._attributes.append(attr)
        self._refresh()

    def set_attributes_from_template(self, attributes: list[Attribute]):
        """
        Fill the list widget with a list of Attributes
        """
        self._attributes = []
        self.clear()
        for attr in attributes:
            # print("from template attr is separator :", isinstance(attr, Separator))
            # print(attr)

            widget = AttributeWidget(attr, parent=self)
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, widget)

            self._attributes.append(attr)
        self._refresh()

    def _refresh(self):
        pass

    def add_attribute(self, attribute: Attribute):
        """
        Add a widget attribute to the ListWidget
        """
        widget = AttributeWidget(attribute, parent=self)

        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)
        self._attributes.append(attribute)

        self._refresh()

    def remove_attribute(self, attribute: Attribute):
        """
        Remove a widget attribute of the ListWidget
        """
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            candidate_attr = widget.attribute
            if candidate_attr == attribute:
                if not candidate_attr.has_connexions:
                    self._attributes.pop(i)
                    self.takeItem(i)
                break


    def selected_attribute(self):
        for i in range(self.count()):
            item = self.item(i)
            if item.isSelected():
                wid = self.itemWidget(item)
                attr: Attribute = wid.attribute
                return attr

    def attributes(self) -> list[Attribute]:
        attributes = []
        for i in range(self.count()):
            item = self.item(i)
            wid = self.itemWidget(item)
            attr : Attribute = wid.attribute
            attributes.append(attr)
        return attributes


class AttributeTemplateIOWidget(QtWidgets.QGroupBox):
    """
    A widget used to import or export attribute template in the Ui
    It is a
    """

    TEMPLATES_NAMES = []

    import_template = QtCore.Signal()
    export_template = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._templates = {}
        self._layout()
        self._load_templates()

    def _layout(self):
        # Combo templates
        self.combo = QtWidgets.QComboBox()

        # Line name
        self.line_template_name = QtWidgets.QLineEdit()
        self.line_template_name.setPlaceholderText("New Template")

        # Button Import
        self.btn_import = QtWidgets.QPushButton("Import selected")
        self.btn_import.clicked.connect(self._on_import_template)

        # Button export
        self.btn_export = QtWidgets.QPushButton("Export new")
        self.btn_export.clicked.connect(self._on_export_template)

        lay = QtWidgets.QHBoxLayout()
        lay.addWidget(self.combo, 1)
        lay.addWidget(self.btn_import)
        lay.addWidget(self.line_template_name)
        lay.addWidget(self.btn_export)

        self.setLayout(lay)
        self.setTitle("Attribute Template")

    def _custom_attribute_templates(self) -> dict:
        try:
            with open(templates_file_path, mode="rb") as template_dict:
                templates = pickle.load(template_dict)
            return templates
        except EOFError:
            return {"None": 0}

    def _load_templates(self):
        """
        Load the pickle file with all attribute templates
        """
        # return
        self._templates = self._custom_attribute_templates()
        self.TEMPLATES_NAMES = self._templates.keys()
        self.combo.addItems(self.TEMPLATES_NAMES)
        self.combo.setCurrentText("None")

    def _on_import_template(self):
        """
        Emit the signal for the main widget to set the attributes with current template
        """
        if self.combo.currentText() == "None":
            print("No template selected")
            return

        self.import_template.emit()

    def _is_export_valid(self) -> bool:
        template_name = self.line_template_name.text()
        if not template_name:
            print("Set a name for the new Template")
            return False
        else:
            return True

    def _on_export_template(self):
        """
        Parse the current attributes and export it as a new template in a pickle file
        """
        if not self._is_export_valid():
            return
        self.export_template.emit()

    def do_export_template(self, template:list[Attribute]):
        """
        Receive a template and export it in a pickle file
        """
        if not self._is_export_valid():
            return
        current_template_name = self.combo.currentText()

        template_name = self.line_template_name.text()
        new_template = {
            template_name : template
        }

        # templates = self._custom_attribute_templates()
        # templates.update(new_template)

        with open(templates_file_path, mode="wb") as template_dict:
            pickle.dump(new_template, template_dict)

        self._load_templates()
        self.combo.setCurrentText(current_template_name)

    def selected_template(self) -> list[Attribute]:
        """
        Return the current template Attributes list
        """
        templates = self._custom_attribute_templates()

        for template_name, template in templates.items():
            if self.combo.currentText() == template_name:
                return template


class AttributeWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    STYLE_SHEET = """
    QPushButton:hover{
      background-color:green
    }
    QListWidget:item:selected {
        border: 2px solid #5096cd;
        border-radius: 5px;
        border-color: "yellow" ;
    }
    QListWidget:item {
        border: 2px solid #5096cd;
        border-radius: 5px;
        border-color: palette(light) ;
    }
    """

    _connect_signals = False

    def __init__(self, parent=None):
        super().__init__()

        self.obj = None

        self._build_layout()

    # region -- Layout
    def _build_layout(self):
        # Header
        _header = HeaderWidget(title = "Attribute Window", color = get_color(2))

        # Line Node
        self._line_node = QtWidgets.QLineEdit()
        self._line_node.setPlaceholderText("Transform Node")

        # Label Node
        self._btn_node = QtWidgets.QPushButton("Define Node")
        self._btn_node.setFixedSize(70, 50)
        self._btn_node.clicked.connect(self._define_obj)

        # Node Layout
        node_box = QtWidgets.QGroupBox("Node")
        node_layout = QtWidgets.QHBoxLayout()
        node_layout.addWidget(self._btn_node)
        node_layout.addWidget(self._line_node)
        node_layout.addStretch()
        node_box.setLayout(node_layout)

        # Attribute List
        self._attr_list = AttributeListWidget()

        # Widget Attribute
        self.wid_add_attr = AddAttributeWidget()
        self.wid_add_attr.add_clicked.connect(self._add_attribute)
        self.wid_add_attr.remove_clicked.connect(self._remove_attribute)

        # Widget Separator
        twid_separator = self._build_wid_separator()

        # Left Layout
        left_box = QtWidgets.QGroupBox("Custom Attributes List")
        left_box.setContentsMargins(0, 0, 0 , 0)
        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._attr_list, 1)
        lay.addWidget(twid_separator)
        left_box.setLayout(lay)
        # left_layout = QtWidgets.QVBoxLayout()
        # left_layout.addWidget(self._attr_list)
        # left_layout.addWidget(tab_attribute)


        # Right Layout
        right_box = QtWidgets.QGroupBox("Add Attribute")
        right_box.setContentsMargins(0, 0, 0, 0)
        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.wid_add_attr)
        right_box.setLayout(lay)
        # right_layout = QtWidgets.QTabWidget()
        # right_layout.addTab(tab_attribute, "Attribute")
        # right_layout.addTab(tab_separator, "Separator")

        # Central Horizontal Layout
        attr_splitter = QtWidgets.QSplitter()
        attr_splitter.addWidget(left_box)
        attr_splitter.addWidget(right_box)
        attr_splitter.setStretchFactor(0, 3)
        attr_splitter.setCollapsible(0, False)
        attr_splitter.setStretchFactor(1, 5)
        attr_splitter.setCollapsible(1, False)

        # Apply Attributes Modifications
        self._apply_btn = QtWidgets.QPushButton("Apply")
        self._apply_btn.setFixedHeight(50)
        self._apply_btn.clicked.connect(self._on_apply)

        # Template
        self._template_widget = AttributeTemplateIOWidget()
        self._template_widget.import_template.connect(self._import_template)
        self._template_widget.export_template.connect(self._export_template)

        # Main Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(_header)
        layout.addWidget(node_box)
        layout.addWidget(attr_splitter, 1)
        layout.addWidget(self._apply_btn)
        layout.addWidget(self._template_widget)
        self.setLayout(layout)

        # Settings
        self.resize(550, 700)
        self.setStyleSheet(self.STYLE_SHEET)


    def _build_wid_separator(self) -> QtWidgets.QGroupBox:
        # Line Separator Name
        self._line_separator = QtWidgets.QLineEdit()
        self._line_separator.setPlaceholderText("Separator Name")

        # Button Add Separator
        self._btn_add_separator = QtWidgets.QPushButton("Add")
        self._btn_add_separator.clicked.connect(self._add_separator)
        # Button Remove Separator
        self._btn_remove_separator = QtWidgets.QPushButton("Remove")
        self._btn_remove_separator.clicked.connect(self._remove_separator)

        # Layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._line_separator)
        layout.addWidget(self._btn_add_separator)
        layout.addWidget(self._btn_remove_separator)
        layout.setContentsMargins(0, 7, 0, 7)
        layout.addStretch()

        group_separator = QtWidgets.QGroupBox("Separator")
        group_separator.setLayout(layout)

        return group_separator

    #endregion
    @property
    def _has_obj(self) -> bool:
        if not self.obj:
            QtWidgets.QMessageBox.warning(self, "No Object", "No Object Selected.")
            print("No Object Selected")
            return False
        else:
            return True

    def _define_obj(self):
        node = select_object(obj=None)
        self.obj = node
        if node: # all nodes receive
            self._attr_list.set_obj(self.obj)
            self._refresh()
        else:
            print("You must select an object")

    def _refresh(self):
        if not self._has_obj:
            return

        self._line_node.setText(self.obj)

        attributes = get_custom_non_hidden_attributes(obj=self.obj)

        self._attr_list.set_attributes_from_node(attributes)

    # Attribute

    @undo_chunk
    def _add_attribute(self, attr: Attribute):
        """ Add a custom attribute in the list widget when hearing the add_clicked signal  """
        if not self._has_obj:
            return
        self._attr_list.add_attribute(attribute=attr)

    @undo_chunk
    def _remove_attribute(self):
        """ Delete a custom attribute from the list widget """
        if not self._has_obj:
            return

        attr = self._attr_list.selected_attribute()
        if isinstance(attr, Separator):
            return
        elif isinstance(attr, Attribute):
            self._attr_list.remove_attribute(attribute=attr)

    # Separator

    @undo_chunk
    def _add_separator(self):
        """
        Add a custom attribute Separator with a custom name in the list widget
        """
        if not self._has_obj:
            return

        separator_name = self._line_separator.text()
        separator = Separator(node=self.obj, separator_name=separator_name)
        self._attr_list.add_attribute(attribute=separator)

        return True

    @undo_chunk
    def _remove_separator(self):
        """
        Remove a attribute Separator with a custom name in the list widget
        """
        if not self._has_obj:
            return
        attr = self._attr_list.selected_attribute()
        if isinstance(attr, Separator):
            self._attr_list.remove_attribute(attribute=attr)
            return True
        else:
            return False


    # Template

    @undo_chunk
    def _import_template(self):
        """
        Fill the ui with attribute from imported template
        """
        attrs_list = self._template_widget.selected_template()

        self._attr_list.set_attributes_from_template(attrs_list)

    @undo_chunk
    def _export_template(self):
        """
        Parse the attribute list and send it to the template widget
        """
        attrs_list = self._attr_list.attributes()
        self._template_widget.do_export_template(attrs_list)

    @undo_chunk
    def _on_apply(self):
        attributes : list[Attribute] = self._attr_list.attributes()

        node = select_object(obj=None)

        attrs_cache_node = create_attribute_cache_node(attrs_list = attributes)

        remove_custom_attributes(obj=node)
        add_custom_attributes(attrs_list=attributes, target_objs=[node], connexion=True)
        cmds.delete(attrs_cache_node)

        select_object(obj=node)

        print("Attributes applied to object")



