from main_hero_class import MainHero


def wall_quest(hero):
    if hero.items["dust"] != 0 and hero.quest == "wall":
        hero.items["dust"] = 0
        hero.get_quest(quests_dict["statue"]["quest"])
        hero.quest = "statue"
        return quests_dict["statue"]["text"]
    if hero.quest == "start":
        hero.quest = "wall"
    return quests_dict["wall"]["text"]


def statue_quest(hero):
    if hero.items["figure"] != 0 and hero.quest == "statue":
        hero.items["statue"] = 0
        hero.get_quest("end")
        return "    Свечение вокруг усиливается..."
    return ""



quests_dict = {
    "wall": {"text": "На стене виднеются углубления похожие на надпись. Вокруг слишком темно, света люмена не "
                     "хватает, чтобы разобрать написанное.",
             "quest": "Прочитайте надпись.",
             "func": wall_quest},
    "statue": {"text": "Размазав прах по стене, стала видна надпись: \"Статуэтка дарует сон великому злу\"",
               "quest": "Найдите статуэтку и отнесите к алтарю.",
               "func": statue_quest}
}