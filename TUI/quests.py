"""
Модуль квестов игры.
"""

from main_hero_class import MainHero


def wall_quest_meeting(hero):
    """
    Функция, обрабатывающая встречу квеста WALL.
    """

    if hero.quest == 'start':
        hero.quest = 'wall'
        hero.current_quest_coordinates = hero.coordinates[:]
        hero.QUEST_CHANGED = True  # Флаг изменения квеста
        return quests_dict["wall"]["text"]
    if hero.quest == 'wall':
        return quests_dict["wall"]["text"]


def wall_quest_completion(hero):
    """
    Функция, проверяющая выполнение квеста WALL
    """

    if hero.items["dust"] != 0 and hero.quest == "wall" and hero.coordinates == hero.current_quest_coordinates:
        hero.items["dust"] = 0
        hero.quest = 'transit'
        quests_dict['wall']['complete'] = True
        return True
    else:
        return


def statue_quest_meeting(hero):
    """
    Функция, обрабатывающая встречу квеста STATUE.
    """

    if quests_dict['wall']['complete'] and hero.quest != 'statue':  # TODO
        hero.quest = 'statue'
        hero.current_quest_coordinates = hero.coordinates[:]
        hero.QUEST_CHANGED = True
        return quests_dict["statue"]["text"]
    elif hero.quest == 'statue':
        return quests_dict["statue"]["text"]
    else:
        return ''


def statue_quest_completion(hero):
    """
    Функция, проверяющая выполнение квеста WALL
    """

    if hero.items['figure'] != 0 and hero.quest == 'statue' and hero.coordinates == hero.current_quest_coordinates:
        hero.items['figure'] = 0
        hero.quest = 'end'
        hero.mind = 100
        quests_dict['statue']['complete'] = True
        return True
    else:
        return


quests_dict = {
    "wall": {"text": "На стене виднеются углубления похожие на надпись. Вокруг слишком темно, света не "
                     "хватает, чтобы разобрать написанное.",
             "quest": "Найдите способ прочесть надпись и вернитесь к резной стене. \nНе заблудитесь в пути...",
             "func": wall_quest_meeting,
             "complete": False},
    "statue": {"text": "...едва уцелевший одинокий постамент. Возможно, Вам удастся наконец найти свое спасение!",
               "quest": "Найдите статуэтку и вознесите ее к алтарю.",
               "func": statue_quest_meeting,
               "complete": False},
    "end": {
            "quest": "Ваши муки окончены.\nА может... это было страшным сном?"}
}
