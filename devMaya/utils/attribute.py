from maya import cmds

def lock_attributes(obj, attr_name: str | list[str]="all"):
    if attr_name == "all":
        for attr in Attribute.KEYABLE_BASE_ATTRIBUTES:
            cmds.setAttr(f'{obj}.{attr}', lock=1)
    else:
        if isinstance(attr_name, str):
            try:
                cmds.setAttr(f'{obj}.{attr_name}', lock=1)
            except:
                return
        if isinstance(attr_name, list):
            for attr in attr_name:
                try:
                    cmds.setAttr(f'{obj}.{attr}', lock=1)
                except:
                    continue
            return

def connect_attributes(obj_src, obj_target, attributes_list: list[str]):
    """
    Utils to connect attributes to make code clearer and quicker
    """
    for attr in attributes_list:
        cmds.connectAttr(f"{obj_src}.{attr}", f"{obj_target}.{attr}")


class Attribute:

    KEYABLE_BASE_ATTRIBUTES: list[str] = [
        "tx",
        "ty",
        "tz",
        "rx",
        "ry",
        "rz",
        "sx",
        "sy",
        "sz",
    ]

    def __init__(self,
                 long_name,
                 nice_name : str =None,
                 type=None,
                 max : float = None,
                 min : float = None,
                 default_value : float = None,
                 enum_names=[],
                 locked=False,
                 keyable=True,
                 attr_dict={},
                 node=None,
                 add_to_node=False):
        self.long_name = long_name
        self.nice_name = nice_name
        self.type = type
        self.locked = locked
        self.keyable = keyable

        self.max = max
        self.min = min
        self.enum_names = enum_names
        self.default_value = default_value

        self.input_connexion:list[str] = []
        self.output_connexions:list[str] = []

        for key, value in attr_dict.items():
            self.__setattr__(key, value)

        self.node = node
        if add_to_node:
            self.add_to_node(node)

    def __str__(self):
        if self.node:
            return f"{self.node}.{self.long_name}"
        else:
            return self.long_name

    def __repr__(self):
        text = f"""
        - Attribute -
        Name: {self.long_name}
        Type: {self.type}
        """
        if self.type == "enum":
            text += f"Enum names :{self.enum_names}"
        return text

    def __del__(self):
        if self.node:
            if self.input_connexion or self.output_connexions:
                return False

    def build_attribute_from_node(self, node):
        """
        Fetch attribute's parameters from node's attribute
        Can return a Separator if it detects this must be a Separator
        """
        self.nice_name = cmds.attributeQuery(self.long_name, node=node, niceName=True)
        self.type = cmds.attributeQuery(self.long_name, node=node, attributeType=True)
        self.keyable = cmds.getAttr(f"{node}.{self.long_name}", k=True)
        if self.type == "enum":
            self.enum_names = cmds.attributeQuery(self.long_name, n=node, listEnum=True)[0].split(":")
            must_be_a_separator = not self.keyable and self.long_name.startswith("__")
            if must_be_a_separator:
                return Separator(node=node, separator_name=self.enum_names[0])

        self.min = cmds.attributeQuery(self.long_name, node=node, min=True)[0] \
            if cmds.attributeQuery(self.long_name, node=node, mne=True) else None
        self.max = cmds.attributeQuery(self.long_name, node=node, max=True)[0] \
            if cmds.attributeQuery(self.long_name, node=node, mxe=True) else None
        self.default_value = cmds.attributeQuery(self.long_name, n=node, listDefault=True)[0]
        self.locked = cmds.getAttr(f"{node}.{self.long_name}", l=True)

        self.node = node
        self.input_connexion = cmds.connectionInfo(f"{node}.{self.long_name}", sourceFromDestination=True)
        self.output_connexions = cmds.connectionInfo(f"{node}.{self.long_name}", destinationFromSource=True)
        return self

    def add_to_node(self, node, connexion=False):
        """
        Add this custom attribute to the provided node
        connexion : if True, create connexions that this attribute holds, but with the node provided instead
        """
        if not cmds.objExists(node):
            print("The provided node does not exist :", node)
            return None

        if cmds.attributeQuery(self.long_name, n=node, exists=True):
            return None

        attr_dict = {
            "longName": self.long_name,
            "k": self.keyable,
            "at": self.type,
        }
        if self.default_value != None:
            attr_dict["dv"] = float(self.default_value)
        if self.max != None:
            attr_dict["maxValue"] = self.max
        if self.min != None:
            attr_dict["minValue"] = self.min
        if self.type == "enum":
            enum_string = ":".join(self.enum_names)
            attr_dict["enumName"] = enum_string

        cmds.addAttr(node, **attr_dict)
        self.node = node

        cmds.setAttr(f"{node}.{self.long_name}", l=self.locked)
        if not self.keyable:
            cmds.setAttr(f"{node}.{self.long_name}", cb=True)

        if connexion:
            if self.input_connexion:
                self.plug_in(self.input_connexion)
            if self.output_connexions:
                for output in self.output_connexions:
                    self.plug_to(output)

    def plug_in(self, attr, force=1):
        cmds.connectAttr(str(attr), str(self), f=force)
        if str(attr) != self.input_connexion:
            self.input_connexion = str(attr)

        # try:
        #     cmds.connectAttr(str(attr), str(self), f=force)
        #     if str(attr) != self.input_connexion:
        #         self.input_connexion = str(attr)
        #     return True
        # except:
        #     return False


    def plug_to(self, attr, force=1):
        cmds.connectAttr(str(self), str(attr), f=force)
        if attr not in self.output_connexions:
            self.output_connexions.append(str(attr))

        # try:
        #     cmds.connectAttr(str(self), str(attr), f=force)
        #     if attr not in self.output_connexions:
        #         self.output_connexions.append(str(attr))
        #     return True
        # except:
        #     return False

    def unplug_to(self, attr):
        try:
            cmds.disconnectAttr(str(self), str(attr))
            if attr in self.output_connexions:
                self.output_connexions.remove(str(attr))
            return True
        except:
            return False

    @property
    def has_connexions(self) -> bool:
        return any([self.input_connexion, self.output_connexions])

class Separator(Attribute):
    def __init__(self, node: str, separator_name: str, type="enum", attr_separation: str="_"):
        for i in range(10):
            unique_attr_name = attr_separation * (i + 3)
            if cmds.attributeQuery(unique_attr_name, exists=True, node=node):
                continue
            else:
                super().__init__(
                    long_name=str(attr_separation * (i + 3)),
                    # nice_name=str(attr_separation * (i + 3)),
                    type=type,
                    enum_names=[separator_name],
                    locked=True,
                    node=node,
                    keyable=False
                )
                break

    def __str__(self):
        if self.node:
            return f"{self.node}.{self.long_name}"
        else:
            return self.long_name

    def __repr__(self):
        text = f"""
        - Separator -
        Name: {self.enum_names[0].upper()}
        """
        return text

    def add_to_node(self, node, connexion=False):
        Separator(node, separator_name=self.enum_names[0])
        super().add_to_node(node=node, connexion=connexion)


def add_separator_attribute(obj: str, separator_name: str, attr_separation: str="_"):
    """
    Create A locked separator enum attribute with custom name
    """
    separator = Separator(node=obj, separator_name=separator_name, attr_separation=attr_separation)
    separator.add_to_node(node=obj, connexion=False)

def get_custom_non_hidden_attributes(obj=None) -> list[str]:
    """
    Get all custom visible attributes of the obj
    """
    if not obj:
        obj = cmds.ls(sl=True)[0]
    
    all_attrs = cmds.listAttr(obj, userDefined=True) or []

    return all_attrs

def remove_custom_attributes(obj=None):
    if not obj:
        obj = cmds.ls(sl=True)[0]

    all_attrs = get_custom_non_hidden_attributes(obj=obj)
    for attr in all_attrs:
        if isinstance(attr, Separator) or cmds.getAttr(f"{obj}.{attr}", lock=True):
            cmds.setAttr(f"{obj}.{attr}", e=1, lock=False)
        cmds.deleteAttr(obj, attribute=attr)

def add_custom_attributes(attrs_list: list[Attribute], target_objs: list[str]=[], connexion=False):
    if target_objs == []: # if no list is provided, use the selected objects ([] if no selection)
        target_objs = cmds.ls(sl=1)

    for obj in target_objs:
        for attr in attrs_list:
            if isinstance(attr, Separator):
                attr = Separator(obj, separator_name=attr.enum_names[0])
            attr.add_to_node(obj, connexion=connexion)

def create_attribute_cache_node(attrs_list : list[Attribute]) -> str:
    """
    Create a temporary obj that will cache attributes and their connexions
    Useful when you want to reorder attributes on another obj
    """
    cache_node = cmds.group(name="cache_node_need_to_be_removed", empty=1)

    add_custom_attributes(attrs_list=attrs_list, target_objs=[cache_node], connexion=True)

    return cache_node

