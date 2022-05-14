"""
Модуль нейронной сети, генерирующей текстовые описания.
"""

from collections import Counter
import numpy
import torch
import pickle


def sequence_create(raw_text):
    """
    Функция для подготовки данных.

    :param raw_text: исходный текст.

    :return:
        sequence: текст в индексах символов;
        char_to_int: словарь для перевода из символа в число;
        int_to_char: словарь для перевода из числа в символ.
    """

    counts_of_chars = Counter(raw_text)
    counts_of_chars = sorted(counts_of_chars.items(), key=lambda x: x[1], reverse=True)
    sorted_chars = [char for char, _ in counts_of_chars]
    # print(sorted_chars)
    char_int = {char: index for index, char in enumerate(sorted_chars)}
    int_char = {v: k for k, v in char_int.items()}
    sequence_of_chars = numpy.array([char_int[char] for char in raw_text])
    return sequence_of_chars, char_int, int_char


SEQ_LEN = 256
BATCH_SIZE = 10


def get_batch(sequence_of_chars):
    """
    Функция для формирования батчей.

    :param sequence_of_chars: послдовательность символов.

    :return: наборы для обучения (значение для передачи и ожидаемые результаты).
    """
    trains = []
    targets = []
    for _ in range(BATCH_SIZE):
        start = numpy.random.randint(0, len(sequence_of_chars) - SEQ_LEN)
        chunk = sequence_of_chars[start: start + SEQ_LEN]
        train_batch = torch.LongTensor(chunk[:-1]).view(-1, 1)
        target_batch = torch.LongTensor(chunk[1:]).view(-1, 1)
        trains.append(train_batch)
        targets.append(target_batch)
    return torch.stack(trains, dim=0), torch.stack(targets, dim=0)


def text_generating(web_model, char_int, int_char, start_text='', prediction_len=200, temp=0.5):
    """
    Функция для формирования текста.

    :param web_model: модель для генерации текста;
    :param char_int: словарь для перевода из символа в число;
    :param int_char: словарь для перевода из числа в символ;
    :param start_text: начальный символ текста;
    :param prediction_len: длина генерируемой последовательности;
    :param temp: коэффициент случайности следующего символа.

    :return: сгенерированный текст.
    """

    hidden_part = web_model.init_hidden()
    int_input = [char_int[char] for char in start_text]
    train_of_chars = torch.LongTensor(int_input).view(-1, 1, 1).to(device)
    prediction_text = start_text

    _, hidden_part = web_model(train_of_chars, hidden_part)

    inp = train_of_chars[-1].view(-1, 1, 1)

    i = 0
    predicted_char = ""
    n = True
    while i < prediction_len or (predicted_char not in ['.', '!', '?']) or n:
        outputting, hidden_part = web_model(inp.to(device), hidden_part)
        output_logits = outputting.cpu().data.view(-1)
        p_next = torch.softmax(output_logits / temp, dim=-1).detach().cpu().data.numpy()
        top_index = numpy.random.choice(len(char_int), p=p_next)
        inp = torch.LongTensor([top_index]).view(-1, 1, 1).to(device)
        predicted_char = int_char[top_index]
        if predicted_char.isupper():
            n = False
        if not n:
            prediction_text += predicted_char
            i += 1
    return prediction_text


class LTSM(torch.nn.Module):
    """
    Класс нейронной сети.
    """

    def __init__(self, input_size, hidden_size, embedding_size, n_layers=1):
        """
        Инициализация аргументов.

        :param input_size: размер входных данных;
        :param hidden_size: сложность сети (данные, недоступные для слоя);
        :param embedding_size: длина числовых векторов;
        :param n_layers: сложность сети (слои).
        """

        super(LTSM, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.embedding_size = embedding_size
        self.n_layers = n_layers

        self.encoder = torch.nn.Embedding(self.input_size, self.embedding_size)
        self.lstm = torch.nn.LSTM(self.embedding_size, self.hidden_size, self.n_layers)
        self.dropout = torch.nn.Dropout(0.2)
        self.fc = torch.nn.Linear(self.hidden_size, self.input_size)

    def forward(self, x, hidden_part):
        x = self.encoder(x).squeeze(2)
        out, (ht1, ct1) = self.lstm(x, hidden_part)
        out = self.dropout(out)
        x = self.fc(out)
        return x, (ht1, ct1)

    def init_hidden(self, batch_size=1):
        return (torch.zeros(self.n_layers, batch_size, self.hidden_size, requires_grad=True).to(device),
                torch.zeros(self.n_layers, batch_size, self.hidden_size, requires_grad=True).to(device))


device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

if __name__ == "__main__":
    continue_flag = 1
    with open("text.txt") as file:
        text = file.readlines()
    text = ' '.join(text)

    sequence, char_to_int, int_to_char = sequence_create(text)
    print(len(sequence))

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model = LTSM(input_size=len(int_to_char), hidden_size=300, embedding_size=128, n_layers=2)
    model.to(device)

    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2, amsgrad=True)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        patience=5,
        verbose=True,
        factor=0.5
    )

    loss_avg = []
    while continue_flag == 1:
        model.train()
        train, target = get_batch(sequence)
        train = train.permute(1, 0, 2).to(device)
        target = target.permute(1, 0, 2).to(device)
        hidden = model.init_hidden(BATCH_SIZE)

        output, hidden = model(train, hidden)
        loss = criterion(output.permute(1, 2, 0), target.squeeze(-1).permute(1, 0))

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        loss_avg.append(loss.item())
        if len(loss_avg) >= 50:
            mean_loss = numpy.mean(loss_avg)
            print(f'Loss: {mean_loss}')
            scheduler.step(mean_loss)
            loss_avg = []
            model.eval()
            predicted_text = text_generating(model, char_to_int, int_to_char)
            print(predicted_text)
            print("Продолжить?")
            continue_flag = int(input())
    torch.save(model.state_dict(), 'entire_model.pt')

    with open('char_to_idx.pickle', 'wb') as f:
        pickle.dump(char_to_int, f)

    with open('idx_to_char.pickle', 'wb') as f:
        pickle.dump(int_to_char, f)
