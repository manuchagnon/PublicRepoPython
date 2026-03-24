import json
import os

"""
Module that make use of custom colors for my UIs
"""

base_dir = os.path.dirname(os.path.abspath(__file__))
colors_file_path = os.path.join(base_dir, "colors_dict.json")

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

    else:
        return default


def run():
    print(get_color(5))

if __name__ == '__main__':
    run()
