"""
Модуль мини-игры с искаженными словами.
"""

from random import randint, random

words = ["AMORPH", "PHYSIOLOGY", "NECRONOMICON", "SCARE", "SCARS", "AMPHIBIAN",
         "MONSTER", "MIND", "DARKNESS", "DEEP", "MYSTERY", "PUZZLE", "BONES"]
signs = "%&@#*№"


def word_make():
    """
    Функция, генерирующая пару (ИСКАЖЕННОЕ СЛОВО, КЛЮЧ)
    """

    flag = False
    word = ''
    raw_word = words[randint(0, len(words) - 1)]

    while not flag:
        flag, word = blur(raw_word)

    return raw_word, word


def blur(raw_word):
    """
    Функция, генерирующая ИСКАЖЕННОЕ СЛОВО
    """

    flag = False
    word = ''
    for i in range(len(raw_word)):
        if randint(0, 75) * random() > 25 and not flag:
            word += signs[randint(0, len(signs) - 1)]
            flag = True
        else:
            word += raw_word[i]
    return flag, word


def word_guess(hero, ans, input):
    """
    Функция, определяющая угадано ли слово.
    Возвращает True в случае удачи и False в противном случае.
    """

    if input.upper() == ans:
        if hero.mind <= 95:
            hero.mind += 5
        return True
    else:
        hero.mind -= 5
        return False
