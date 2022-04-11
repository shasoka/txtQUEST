from main_hero_class import MainHero
import json
import random

with open("Map_generator/map.json", "r", encoding="UTF-8") as f:
    map_of_world = json.load(f)


def description_output(coordinates, mind):
    output = ""
    raw_output = map_of_world[coordinates[0]][coordinates[1]]["map"]
    signs = "%&@#*№"
    for char in raw_output:
        if char != " " and random.randint(0, 75) * random.random() > mind:
            output += random.choice(signs)
        else:
            output += char
    if map_of_world[coordinates[0]][coordinates[1]]["statue"] == 1:
        output += "\n Огромная статуя, повторяющая изображение на фигурке"
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


def show_items(items_dict):
    for thing, num in items_dict.items():
        if num:
            print(thing, ": ", num, sep="")


def find_items(items_dict):
    items = 0
    for item, amount in items_dict.items():
        if amount != [0] and item not in ["map", "statue"]:
            items += 1
    if items > 0:
        print("Осмотреть предметы - items")


def take_item(name):
    if name in hero.items and name in map_of_world[hero.coordinates[0]][hero.coordinates[1]]["items"]:
        hero.items[name] += 1
    elif name in map_of_world[hero.coordinates[0]][hero.coordinates[1]]:
        hero.items[name] = 1
    map_of_world[hero.coordinates[0]][hero.coordinates[1]]["items"][name] -= 1


def show_inventory(inventory):
    for item, num in inventory.items():
        if num != 0:
            print(item, ": ", num, sep="")


hero = MainHero()

commands = {
    "move": hero.move,
    "items": show_items,
    "take": take_item,
    "show": show_inventory
}

while (n := str(input())) != '0':
    print(map_of_world[hero.coordinates[0]][hero.coordinates[1]]["statue"], hero.items["figure"])
    if map_of_world[hero.coordinates[0]][hero.coordinates[1]]["statue"] == 1 and hero.items["figure"] == 1:
        print("End")
        break
    if n in ["up", "down", "right", "left"]:
        commands["move"](n)
    elif n == "items":
        commands[n](map_of_world[hero.coordinates[0]][hero.coordinates[1]]["items"])
        take_item(n := str(input()))
        continue
    elif n == "show":
        commands[n](hero.items)
        continue

    print(hero.coordinates)
    print(description_output(hero.coordinates, hero.mind), "\n")
    print(mind_output(hero.mind))
    find_items(map_of_world[hero.coordinates[0]][hero.coordinates[1]])
