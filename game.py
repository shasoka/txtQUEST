from main_hero_class import MainHero
import json
import random

with open("Map_generator/map.json", "r", encoding="UTF-8") as f:
    map_of_world = json.load(f)


def description_output(coordinates, mind):
    output = ""
    raw_output = map_of_world[str(coordinates[0])][str(coordinates[1])]
    signs = "%&@#*№"
    for char in raw_output:
        if char != " " and random.randint(0, 75) * random.random() > mind:
            output += random.choice(signs)
        else:
            output += char
    return output


def mind_output(mind):
    if 75 >= mind > 50:
        return "Я слышу чье-то дыхание, возможно я просто переутомился."
    elif 50 >= mind > 25:
        return "Порой мне кажется, что кто-то говорит со мной."
    elif mind <= 25:
        return "Голос в голове не дает мне ясно думать."
    else:
        return "Нужно продолжать исследования."


hero = MainHero()

while (n := str(input())) != '0':
    hero.move(n)
    hero.mind -= 10
    print(hero.coordinates)
    print(description_output(hero.coordinates, hero.mind), "\n")
    print(mind_output(hero.mind))
