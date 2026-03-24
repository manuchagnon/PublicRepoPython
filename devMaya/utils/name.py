from maya import cmds



"""
Function that deals with naming:
    - replace character in names
"""


def replace_in_names(name_list: list[str], target_str: str, replace_by_str: str):
    """
    Rename a list (long names or names) by replacing target_str with replace_by_str
    """
    for long_name in name_list:
        short_name = long_name.rsplit("|", 1)[-1]
        if target_str in short_name:

            new_name = short_name.replace(target_str, replace_by_str)
            cmds.rename(long_name, new_name)