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
import os

from AI.text_generator import text_generating
from AI.text_generator import LTSM

if __name__ == '__main__':

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    with open(f'{str(os.path.abspath(__file__))[:-20]}/MAP/AI/data/char_to_idx.pickle', 'rb') as f:  # Загрузка модели и данных для генерации текста
        char_to_int = pickle.load(f)
    with open(f'{str(os.path.abspath(__file__))[:-20]}/MAP/AI/data/idx_to_char.pickle', 'rb') as f:
        int_to_char = pickle.load(f)
    model = LTSM(input_size=len(int_to_char), hidden_size=300, embedding_size=128, n_layers=2)
    model.load_state_dict(torch.load(f"{str(os.path.abspath(__file__))[:-20]}/MAP/AI/data/entire_model.pt"))

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
                                        "dust": random.choices([0, 1], weights=[80, 20])[0],
                                             }
                                    })

    map_of_world[random.randint(0, 9)][random.randint(0, 9)]["items"]["figure"] = 1
    map_of_world[random.randint(0, 9)][random.randint(0, 9)]["wall"] = 1
    map_of_world[random.randint(0, 9)][random.randint(0, 9)]["statue"] = 1

    with open(f"{str(os.path.abspath(__file__))[:-20]}/MAP/data/map.json", 'w') as file:  # Сохранение в формате json
        json.dump(map_of_world, file)
