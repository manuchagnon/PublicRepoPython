from maya import cmds

attr_list = [
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

def lock_attributes(obj, attr_name="all"):

    if attr_name == "all":
        for attr in attr_list:
            cmds.setAttr(f'{obj}.{attr}', lock=1)
    elif attr_name in attr_list:
        cmds.setAttr(f'{obj}.{attr_name}', lock=1)
    else:
        return


# for attribute tool, not finished yet
def get_custom_non_hidden_attributes(obj=None) -> list[str]:
    """ Get all custom visible attributes of the first selected obj """
    if not obj:
        obj = cmds.ls(sl=True)[0]
    
    all_attrs = cmds.listAttr(obj, userDefined=True) or []
    
    if not all_attrs:
        cmds.warning("No custom attributes found.")

    attrs_list = [
        attr for attr in all_attrs
        if cmds.getAttr(f"{obj}.{attr}", keyable=True) or cmds.getAttr(f"{obj}.{attr}", channelbox=True)
    ]

    return attrs_list

def get_attributes_data(obj, attr_list: list[str]) -> dict[str, dict]:
    """
    Return attribute metadata (min, max, default, type) for given attributes 
    """
    attr_data_dict = {}

    for attr in attr_list:
        attr_data_dict[attr] = {
            "min": cmds.attributeQuery(attr, n=obj, min=True)[0]
            if cmds.attributeQuery(attr, n=obj, mne=True) else None,

            "max": cmds.attributeQuery(attr, n=obj, max=True)[0]
            if cmds.attributeQuery(attr, n=obj, mxe=True) else None,

            "default": cmds.attributeQuery(attr, n=obj, listDefault=True)[0],
            "type": cmds.attributeQuery(attr, n=obj, attributeType=True),
            "keyable": cmds.getAttr(f"{obj}.{attr}", k=True),
            "locked": cmds.getAttr(f"{obj}.{attr}", l=True)
        }

        if attr_data_dict[attr].get("type") == "enum":
            attr_data_dict[attr]["enum_list"] = cmds.attributeQuery(attr, obj=obj, listEnum=True)[0].split(":")

    return attr_data_dict

def add_custom_attributes(attrs_data_dict: dict, target_objs: list[str]):
    """ Add custom attributes to selected objs """
    cmds.undoInfo(openChunk=True)

    for obj in target_objs:
        for attr, data_type in attrs_data_dict.items():
            if cmds.attributeQuery(attr, n=obj, exists=True):
                continue

            kwargs = {
                "longName": attr,
                "k": data_type["keyable"],
                "attributeType": data_type["type"],
                "dv": data_type.get("default"),
            }

            if data_type.get("min") is not None:
                kwargs["min"] = data_type["min"]

            if data_type.get("max") is not None:
                kwargs["max"] = data_type["max"]

            if data_type.get("type") == "enum":
                enum_string = ":".join(attrs_data_dict[attr]["enum_list"])
                kwargs["enumName"] = enum_string

            cmds.addAttr(obj, **kwargs)

            # Set lock and non-keyable attributes
            cmds.setAttr(f"{obj}.{attr}", l=data_type.get("locked", False))
            if not data_type.get("keyable", True):
                cmds.setAttr(f"{obj}.{attr}", cb=True)

    cmds.undoInfo(closeChunk=True)

def add_separator_attribute(attrs_data_dict: dict):
    """ Adds new separator attribute with title """
    pass

def create_attribute_cache_obj(attrs_data_dict):
    """ Create a temporary obj that will cache attributes before reordering them """
    pass
    

