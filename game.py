import json
import random
from main_hero_class import MainHero
from quests import quests_dict
from words import word_guess

with open("Map_generator/map.json", "r", encoding="UTF-8") as f:
    map_of_world = json.load(f)


def description_output(coordinates, mind):
    output = "    "
    raw_output = map_of_world[coordinates[0]][coordinates[1]]["map"]
    signs = "%&@#*№"
    for char in raw_output:
        if char != " " and random.randint(0, 75) * random.random() > mind:
            output += random.choice(signs)
        else:
            output += char
    for tag, text in map_of_world[coordinates[0]][coordinates[1]].items():
        if tag != "map" and text == 1 and tag in quests_dict:
            output += "\n    " + quests_dict[tag]["func"](hero)
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
    for thing, num in items_dict["items"].items():
        if num:
            print(thing, ": ", num, sep="")


def find_items(items_dict):
    items = 0
    for item, amount in items_dict["items"].items():
        # print(items_dict["items"].items())
        # print(item, amount)
        if amount != 0:
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


def main():
    print(description_output(hero.coordinates, hero.mind), "\n")
    while (n := str(input())) != '0':
        if n in ["up", "down", "right", "left"]:
            commands["move"](n)
            if hero.mind < 95 and random.randint(0, 100) > 70:
                word_guess(hero.mind)
                print(hero.mind)
        elif n == "items":
            commands[n](map_of_world[hero.coordinates[0]][hero.coordinates[1]])
            take_item(n := str(input()))
            continue
        elif n == "show":
            commands[n](hero.items)
            continue

        print(hero.coordinates)
        print(description_output(hero.coordinates, hero.mind), "\n")
        print(mind_output(hero.mind))
        find_items(map_of_world[hero.coordinates[0]][hero.coordinates[1]])


if __name__ == "__main__":
    main()
