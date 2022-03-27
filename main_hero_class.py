class MainHero:
    coordinates = [5, 0]

    def __init__(self):
        self.mind = 100

    def move(self, command):

        if command == "up" and self.coordinates[1] <= 8:
            self.coordinates[1] += 1
        elif command == "down" and self.coordinates[1] >= 0:
            self.coordinates[1] -= 1
        elif command == "left" and self.coordinates[0] >= 1:
            self.coordinates[0] -= 1
        elif command == "right" and self.coordinates[0] <= 8:
            self.coordinates[0] += 1

