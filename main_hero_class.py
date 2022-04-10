import random


class MainHero:
    coordinates = [5, 0]

    def __init__(self):
        self.mind = 100
        self.items = {"light": 1, "figure": 0}

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
            self.items["light"] -= 1
        elif random.randint(0, 100) > 80:
            self.mind -= 10
