"""
Модуль, генерирующий карту.
Во время разработки запускается вручную для обновления карты.
В собранной версии игры карта обновляется автоматически, все ключевые предметы и квесты спавнятся рандомно.
-*- Ключевые элементы карты в релизной версии зафиксированы! -*-
"""

import torch
import pickle
import random
import json
from AI.text_generator import text_generating
from AI.text_generator import LTSM

if __name__ == '__main__':

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    with open('../MAP/AI/char_to_idx.pickle', 'rb') as f:  # Загрузка модели и данных для генерации текста
        char_to_int = pickle.load(f)
    with open('../MAP/AI/idx_to_char.pickle', 'rb') as f:
        int_to_char = pickle.load(f)
    model = LTSM(input_size=len(int_to_char), hidden_size=300, embedding_size=128, n_layers=2)
    model.load_state_dict(torch.load("../MAP/AI/entire_model.pt"))

    alphabet = "абвгдежзийклмнопрстуфхцчшщыэюя"  # Начала строк для генерации текста
    map_of_world = []  # Словарь для описаний локаций по координатам

    for x in range(10):  # Заполнение словаря описаниями
        map_of_world.append([])
        for y in range(10):
            map_of_world[x].append({"map": text_generating(model,
                                                           char_to_int,
                                                           int_to_char,
                                                           temp=0.5,
                                                           prediction_len=150,
                                                           start_text=" " + random.choice(alphabet))[2:],
                                    "statue": 0,
                                    "items": {
                                        "light": random.choices([0, 1], weights=[80, 20])[0],
                                             }
                                    })

    n = random.randint(0, 9)
    m = random.randint(0, 9)
    q = random.randint(0, 9)
    e = random.randint(0, 9)

    map_of_world[5][2]["items"]["figure"] = 1
    map_of_world[5][3]["items"]["dust"] = 1
    map_of_world[5][4]["statue"] = 1
    map_of_world[5][1]["wall"] = 1

    with open("../MAP/map.json", 'w') as file:  # Сохранение в формате json
        json.dump(map_of_world, file)