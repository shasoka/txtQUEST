from collections import Counter
import numpy

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
	counts_of_chars = Counter(text)
	counts_of_chars = sorted(counts_of_chars.items(), key=lambda x: x[1], reverse=True)
	sorted_chars = [char for char, _ in counts_of_chars]
	# print(sorted_chars)
	char_to_int = {char: index for index, char in enumerate(sorted_chars)}
	int_to_char = {v: k for k, v in char_to_int.items()}
	sequence = numpy.array([char_to_int[char] for char in text])
	return sequence, char_to_int, int_to_char

# print(sequence_create(text))
