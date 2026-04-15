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


def replace_in_names(name_list: list[str], target_str: str="", replace_by_str: str=""):
    """
    Rename a list (long names or names) by replacing target_str with replace_by_str
    """
    if not name_list:
        name_list = cmds.ls(sl=1, long=True)

    for long_name in name_list:
        short_name = get_short_name(long_name)

        if target_str in short_name:
            new_name = short_name.replace(target_str, replace_by_str)
            cmds.rename(long_name, new_name)


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


def rename_and_increment(name_list: list[str], base_name: str="", start_index: int=0, padding=2):
    """
    Rename and increment by adding the index at the end
    """
    if not name_list:
        name_list = cmds.ls(sl=1, long=True)

    if padding < 1:
        padding = 1

    for i, long_name in zip(range(len(name_list), 0, -1), name_list[::-1]):
        short_name = get_short_name(long_name)

        index = f"{i:{padding}}".replace(' ', '0')
        new_name = f"{base_name}{index}"

        cmds.rename(long_name, new_name)

