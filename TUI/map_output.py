"""
Тестовый модуль для работы с текстовой версией игры без интерфейса.
Содержит в себе используемую в TUI функцию description_output.
"""

import json
import random


def load_map():
    """
    Функция, загружающая карту из файла.
    """

    with open("../Map_generator/map.json", "r", encoding="UTF-8") as f:
        loaded_map = json.load(f)
    return loaded_map


def description_output(hero, map_of_world, quests_dict):
    """
    Функция, создающая строку, выводимую в главный Speaker игрового интерфейса.
    """

    output = "    "
    raw_output = map_of_world[hero.coordinates[0]][hero.coordinates[1]]["map"]
    signs = "%&@#*№"
    for char in raw_output:
        if char != " " and random.randint(0, 75) * random.random() > hero.mind:
            output += random.choice(signs)
        else:
            output += char
    for map_key, val in map_of_world[hero.coordinates[0]][hero.coordinates[1]].items():
        if map_key != "map" and val == 1 and map_key in quests_dict:
            try:  # Загадочная конкатенация с NoneType, которую я так и не отыскал...
                output += "\n    " + quests_dict[map_key]["func"](hero, quests_dict)
            except TypeError:
                continue
    return output
