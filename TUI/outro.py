"""
Модуль с анимацией эпилога.
"""

import os
import time
from ctypes import *

from asciimatics.effects import Print, Snow, Wipe, Stars
from asciimatics.renderers import ImageFile
from asciimatics.scene import Scene
from asciimatics.screen import Screen, KeyboardEvent, StopApplication


def stop_key(event):
    """
    Обработчик нажатия X для выхода из интро.
    """

    if isinstance(event, KeyboardEvent):
        c = event.key_code
        if c in (ord("X"), ord("x"), ord("ч"), ord("Ч")):
            raise StopApplication("ANIMATION CLOSED. MAIN WINDOW WILL BE OPENED INSTEAD.")


def main_scr(screen):
    """
    Функция, передаваемая в wrapper. Поочередно выводит надписи и анимации.
    """

    screen.print_at(u'Вы очнулись от глубокого сна.', screen.width // 2 - 16, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(4)
    screen.clear()

    screen.print_at(u'Остается только гадать, что же это было . . . ', screen.width // 2 - 23, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(5)
    screen.clear()

    screen.print_at(u'"Вот значит как. Мое погружение было настоящим, я заложник морских глубин . . . "', screen.width // 2 - 40, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(5)
    screen.clear()

    screen.print_at(u'"А ведь так хотелось перед смертью отхлебнуть глоток горького немецкого пива! . . "', screen.width // 2 - 41, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(5)
    screen.clear()

    screen.print_at(u'"Кислород заканчивается. Прощай ХРАМ тайн и ужаса . . . "', screen.width // 2 - 28, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(5)
    screen.clear()

    screen.print_at(u'Сохранение будет удалено. Храм и дальше будет хранить свои секреты . . . ', screen.width // 2 - 35, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(5)
    screen.clear()

    screen.print_at(u'Нажмите "X", чтобы вернуться в меню . . .', screen.width // 2 - 20, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(2)
    screen.clear()

    effects = [
        Print(
            screen,
            ImageFile("outro.jpg", height=25),
            screen.height // 2 - 13),
        Snow(screen),
        Wipe(screen),
        Stars(screen, count=100)
    ]

    screen.play([Scene(effects, 500)], unhandled_input=stop_key)


if __name__ == '__main__':
    x = (windll.user32.GetSystemMetrics(0)) // 5
    y = (windll.user32.GetSystemMetrics(1)) // 5
    os.system('mode con cols=' + str(x) + ' lines=' + str(y))

    Screen.wrapper(main_scr)
