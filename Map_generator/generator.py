import torch
import pickle
import random
import json
from Description_generator.text_generator import text_generating
from Description_generator.text_generator import LTSM

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

"""Загрузка модели и данных для генерации текста"""
with open('../Description_generator/char_to_idx.pickle', 'rb') as f:
    char_to_int = pickle.load(f)
with open('../Description_generator/idx_to_char.pickle', 'rb') as f:
    int_to_char = pickle.load(f)
model = LTSM(input_size=len(int_to_char), hidden_size=300, embedding_size=128, n_layers=2)
model.load_state_dict(torch.load("../Description_generator/entire_model.pt"))

alphabet = "абвгдежзийклмнопрстуфхцчшщыэюя"  # Начала строк для генерации текста
map_of_world = []  # Словарь для описаний локаций по координатам

# Заполнение словаря описаниями
for x in range(10):
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
print(n, m, q, e)


map_of_world[5][1]["items"]["figure"] = 1
map_of_world[5][2]["statue"] = 1

# Сохранение в формате json
with open("map.json", 'w') as file:
    json.dump(map_of_world, file)
