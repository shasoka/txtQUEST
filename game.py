from main_hero_class import MainHero
import json

with open("Map_generator/map.json", "r", encoding="UTF-8") as f:
    map_of_world = json.load(f)

hero = MainHero()
print(map_of_world)
while (n := str(input())) != '0':
    hero.move(n)
    print(hero.coordinates)
    print(map_of_world[str(hero.coordinates[0])][str(hero.coordinates[1])])
