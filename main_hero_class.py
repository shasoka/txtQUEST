import random


class MainHero:
    def __init__(self):
        self.quest = "start"
        self.mind = 100
        self.coordinates = [5, 0]
        self.items = {"light": 0, "figure": 0, "dust": 0}  # Текущее состояние инвентаря

    def move(self, command):
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
            self.mind -= 10

    def get_quest(self, quest_tag):
        self.quest = quest_tag
