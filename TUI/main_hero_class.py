"""
Модуль, содержащий класс персонажа
"""

import random


class MainHero:
    """
    Класс персонажа.

    Атрибуты:
        - mind: int - состояние рассудка;
        - coordinates: list[int] - текущие координаты на карте;
        - items: dict - словарь предметов вида str: int;
        - quest: string - текущий квест;
        - current_quest_coordinate: list[int] - координаты текущего квеста;
        - QUEST_CHAGED: bool - флаг изменения квеста.
    """

    def __init__(self):
        self.quest = "start"
        self.current_quest_coordinates = None
        self.QUEST_CHANGED = False
        self.coordinates = [5, 0]
        self.mind = 100
        self.items = {"light": 0, "figure": 0, "dust": 0}  # Текущее состояние инвентаря

    def move(self, command):
        """
        Метод, обрабатывабщий передвижения игрока по карте.
        """

        if command == "up" and self.coordinates[1] <= 8:
            self.coordinates[1] += 1
        elif command == "down" and self.coordinates[1] >= 0:
            self.coordinates[1] -= 1
        elif command == "left" and self.coordinates[0] >= 1:
            self.coordinates[0] -= 1
        elif command == "right" and self.coordinates[0] <= 8:
            self.coordinates[0] += 1
        if self.items["light"] != 0:
            if random.randint(0, 100) > 90:
                self.items["light"] -= 1
        elif random.randint(0, 100) > 90:
            if self.mind != 0:
                self.mind -= 10
