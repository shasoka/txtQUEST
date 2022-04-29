from random import choice, randint, random

words = ["СТРАХ", "ОНИ", "БОЛЬ", "БОГИ", "БЕЗДНА", "ПАМЯТЬ", "СВЕЧЕНИЕ", "РИТУАЛ", "КУЛЬТ"]
signs = "%&@#*№"


def word_make():
    raw_word = list(choice(words))
    word = ""
    for i in range(len(raw_word)):
        if randint(0, 75) * random() > 25:
            word += choice(signs)
        else:
            word += raw_word[i]
    return word, raw_word


def word_guess(mind, words_list=word_make()):
    ans = "".join(i for i in words_list[1])
    word = words_list[0]
    print("Голоса в голове без остановки повторяют ", word, ".", sep="")
    input_word = str(input())
    if input_word.upper() == ans:
        print("Вы чувствуете, что не все потеряно.")
        if mind + 10 <= 100:
            mind += 10
    else:
        print("Мысли спутываюстся все больше")
        mind -= 5



