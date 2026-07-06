from maya import cmds

"""
Function that deals with naming:
    - replace character in names
    - add suffix str at end of names
    - add prefix str at beginning of names
    - rename and increment
"""

def get_short_name(long_name: str) -> str:
    """
    Always return a short name from a long_name
    """
    return long_name.rsplit("|", 1)[-1]


def replace_in_names(name_list: list[str], target_str: str="", replace_by_str: str="") -> list[str]:
    """
    Rename a list (long names or names) by replacing target_str with replace_by_str
    """
    if not name_list:
        name_list = cmds.ls(sl=1, long=True)

    new_name_list = []
    for long_name in name_list:
        short_name = get_short_name(long_name)

        if target_str in short_name:
            new_name = short_name.replace(target_str, replace_by_str)
            cmds.rename(long_name, new_name)
            new_name_list.append(new_name)
    return new_name_list


def add_to_names(name_list: list[str], added_str: str="", index=-1):
    """
    Add str to names at given index
    """
    if not name_list:
        name_list = cmds.ls(sl=1, long=True)

    for long_name in name_list[::-1]:
        short_name = get_short_name(long_name)

        if index >= 0:
            edited_name = short_name[:index] + added_str + short_name[index:]
            cmds.rename(long_name, edited_name)
        else:
            edited_name = short_name[:index:-1] + added_str[::-1] + short_name[index::-1]
            cmds.rename(long_name, edited_name[::-1])


def rename_and_increment(name_list: list[str], base_name: str="", start_index: int=0, padding=2) -> list[str]:
    """
    Rename and increment by adding the index at the end
    """
    if not name_list:
        name_list = cmds.ls(sl=1, long=True)

    if padding < 1:
        padding = 1

    new_name_list = []
    for i, long_name in zip(range(len(name_list), 0, -1), name_list[::-1]):
        short_name = get_short_name(long_name)

        index = f"{i:{padding}}".replace(' ', '0')
        new_name = f"{base_name}{index}"

        cmds.rename(long_name, new_name)
        new_name_list.append(new_name)

    return new_name_list[::-1]


def get_name_part(full_name) -> str:
    """
    Use to get the alphabetical part of a full name, without numbers at the end
    """
    while full_name[-1].isdigit():
        full_name = full_name[:-1]

    while full_name[-1] == "_":
        full_name = full_name[:-1]

    return full_name


def determine_component_name(base_name:str, prefix:str = "", suffix:str = "", side_suffixes:list[str, str]=[]) -> str:
    """
    Build name for component such as joints or follicule that haven't Component object created yet
    """
    if prefix and prefix in base_name:
        if prefix + "_" in base_name:
            base_name = base_name.replace(prefix + "_", '')
        base_name = base_name.split(prefix)[-1]

    if suffix and suffix in base_name:
        if suffix + "_" in base_name:
            base_name = base_name.replace(suffix + "_", '')
        base_name = base_name.split(suffix)[0]

    has_side_one, has_side_two = side_suffixes[0] in base_name, side_suffixes[-1] in base_name
    if has_side_one:
        if side_suffixes[0] + "_" in base_name:
            base_name = base_name.replace(side_suffixes[0] + "_", '')
        elif base_name.endswith(side_suffixes[0]):
            base_name = base_name.split(side_suffixes[0])[0]
        else:
            base_name = base_name.replace(side_suffixes[0], '')
        return prefix + base_name + suffix + side_suffixes[0]

    elif has_side_two:
        if side_suffixes[1] + "_" in base_name:
            base_name = base_name.replace(side_suffixes[1] + "_", '')
        elif base_name.endswith(side_suffixes[1]):
            base_name = base_name.split(side_suffixes[1])[0]
        else:
            base_name = base_name.replace(side_suffixes[1], '')
        return prefix + base_name + suffix + side_suffixes[1]

    return prefix + base_name + suffix


def determine_base_name(name: str, prefix:str = "", suffix:str = "", side_suffixes:list[str, str]=[]) -> str:
    """
    Empty provided name from any prefix or suffix or side_suffixes
    """
    if prefix and prefix in name:
        if prefix + "_" in name:
            name = name.replace(prefix + "_", '')
        name = name.split(prefix)[-1]

    if suffix and suffix in name:
        if suffix + "_" in name:
            name = name.replace(suffix + "_", '')
        name = name.split(suffix)[0]

    has_side_one, has_side_two = side_suffixes[0] in name, side_suffixes[-1] in name
    if has_side_one:
        if side_suffixes[0] + "_" in name:
            name = name.replace(side_suffixes[0], '_')
        name = name.split(side_suffixes[0])[0]

    elif has_side_two:
        if side_suffixes[-1] + "_" in name:
            name = name.replace(side_suffixes[-1], '_')
        name = name.split(side_suffixes[-1])[0]

    while "__" in name:
        name = name.replace("__", '_')

    if name.endswith("_"):
        name = name[:-1]

    return name

