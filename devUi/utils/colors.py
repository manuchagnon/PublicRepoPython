import json
import os

"""
Module that make use of custom colors
"""

base_dir = os.path.dirname(os.path.abspath(__file__))
colors_file_path = os.path.join(base_dir, "colors_dict.json")

class Colors(dict):
    """
    Container for Colors
    Implement type hint for color
    """
    COLORS_LIST = {}
    _instance = None
    CHANNELS = ("R", "G", "B")

    @classmethod
    def _load(cls):
        if not cls.COLORS_LIST:
            cls.COLORS_LIST = ctl_custom_colors()

    @classmethod
    def keys(cls) -> list[str]:
        cls._load()
        return cls.COLORS_LIST.keys()

    @classmethod
    def get_color(cls, color: str | int | tuple[int, int, int], default=(100, 100, 100)) -> tuple[int, int, int]:
        if isinstance(color, str):
            color = cls.COLORS_LIST.get(color, default)
        elif isinstance(color, int):
            for i, key in enumerate(cls.COLORS_LIST.keys()):
                if i == color:
                    color = cls.COLORS_LIST[key]
                    break
                else:
                    color = default
        return color

    @classmethod
    def __getitem__(cls, key) -> dict[list[list]] | None:
        cls._load()
        return cls.get_color(key)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load()
        return cls._instance

def ctl_custom_colors() -> dict:
    # colors_file_path = r"C:\Documents\2_GIT\MyRepo\devUi\utils\colors_dict.json"

    with open(colors_file_path, mode="r", encoding='utf-8') as colors_dict:
        colors = json.load(colors_dict)
    return colors

# to bo removed
def color_dict():
    with open(colors_file_path , mode="r", encoding='utf-8') as colors_dict:
        return json.load(colors_dict)

def get_color(color: int | str, default= (100, 100, 100) ):

    with open(colors_file_path , mode="r", encoding='utf-8') as colors_dict:
        colors = json.load(colors_dict)

    if isinstance(color, str):
        return colors.get(color, default)

    elif isinstance(color, int):
        for i, key in enumerate(colors.keys()):
            if i == color:
                return colors[key]

    elif isinstance(color, tuple):
        try:
            return (color[0], color[1], color[2])
        except:
            pass
        return default

    else:
        pass

