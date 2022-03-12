from collections import Counter
import numpy
import torch

with open("text.txt") as file:
    text = file.readlines()
text = ' '.join(text)


def sequence_create(raw_text):
    """
    Функция для подготовки данных
    :param raw_text: исходный текст
    :return:
        sequence: текст в индексах символов
        char_to_int: словарь для перевода из символа в число
        int_to_char: словарь для перевода из числа в символ
    """
    counts_of_chars = Counter(raw_text)
    counts_of_chars = sorted(counts_of_chars.items(), key=lambda x: x[1], reverse=True)
    sorted_chars = [char for char, _ in counts_of_chars]
    # print(sorted_chars)
    char_int = {char: index for index, char in enumerate(sorted_chars)}
    int_char = {v: k for k, v in char_int.items()}
    sequence_of_chars = numpy.array([char_int[char] for char in text])
    return sequence_of_chars, char_int, int_char


sequence, char_to_int, int_to_char = sequence_create(text)
print(len(sequence))

SEQ_LEN = 256
BATCH_SIZE = 10


def get_batch(sequence_of_chars):
    """
    Функция для формирования батчей
    :param sequence_of_chars: послдовательность символов
    :return: наборы для обучения (значение для передачи и ожидаемые результаты)
    """
    trains = []
    targets = []
    for _ in range(BATCH_SIZE):
        start = numpy.random.randint(0, len(sequence_of_chars) - SEQ_LEN)
        chunk = sequence_of_chars[start: start + SEQ_LEN]
        train = torch.LongTensor(chunk[:-1]).view(-1, 1)
        target = torch.LongTensor(chunk[1:]).view(-1, 1)
        trains.append(train)
        targets.append(target)
    return torch.stack(trains, dim=0), torch.stack(targets, dim=0)


def text_generating(model, char_int, int_char, start_text=' ', prediction_len=200, temp=0.3):
    """
    Функция для формирования текста
    :param model: модель для генерации текста
    :param char_int: словарь для перевода из символа в число
    :param int_char: словарь для перевода из числа в символ
    :param start_text: начальный символ текста
    :param prediction_len: длина генерируемой последовательности
    :param temp: коэффициент случайности следующего символа
    :return: сгенерированный текст
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    hidden = model.init_hidden()
    int_input = [char_int[char] for char in start_text]
    train = torch.LongTensor(int_input).view(-1, 1, 1).to(device)
    predicted_text = start_text

    _, hidden = model(train, hidden)

    inp = train[-1].view(-1, 1, 1)

    for i in range(prediction_len):
        output, hidden = model(inp.to(device), hidden)
        output_logits = output.cpu().data.view(-1)
        p_next = torch.softmax(output_logits / temp, dim=-1).detach().cpu().data.numpy()
        top_index = numpy.random.choice(len(char_int), p=p_next)
        inp = torch.LongTensor([top_index]).view(-1, 1, 1).to(device)
        predicted_char = int_char[top_index]
        predicted_text += predicted_char
    return predicted_text
