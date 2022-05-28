"""
Модуль квестов игры.
"""

from TUI.main_hero_class import MainHero


def wall_quest_meeting(hero, current_dict):
    """
    Функция, обрабатывающая встречу квеста WALL.
    """

    if hero.quest == 'start':
        hero.quest = 'wall'
        hero.current_quest_coordinates = hero.coordinates[:]
        hero.QUEST_CHANGED = True  # Флаг изменения квеста
        return current_dict["wall"]["text"]
    if hero.quest == 'wall':
        return current_dict["wall"]["text"]


def wall_quest_completion(hero, current_dict):
    """
    Функция, проверяющая выполнение квеста WALL
    """

    if hero.items["dust"] != 0 and hero.quest == "wall" and hero.coordinates == hero.current_quest_coordinates:
        hero.items["dust"] = 0
        hero.quest = 'transit'
        current_dict['wall']['complete'] = True
        return True
    else:
        return


def statue_quest_meeting(hero, current_dict):
    """
    Функция, обрабатывающая встречу квеста STATUE.
    """

    if current_dict['wall']['complete'] and hero.quest != 'statue':
        hero.quest = 'statue'
        hero.current_quest_coordinates = hero.coordinates[:]
        hero.QUEST_CHANGED = True
        return current_dict["statue"]["text"]
    elif hero.quest == 'statue':
        return current_dict["statue"]["text"]
    else:
        return ''


def statue_quest_completion(hero, current_dict):
    """
    Функция, проверяющая выполнение квеста WALL
    """

    if hero.items['figure'] != 0 and hero.quest == 'statue' and hero.coordinates == hero.current_quest_coordinates:
        hero.items['figure'] = 0
        hero.quest = 'end'
        hero.mind = 100
        current_dict['statue']['complete'] = True
        return True
    else:
        return
