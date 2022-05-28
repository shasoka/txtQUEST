"""
Модуль с анимацией при проигрыше.
"""

import os
import time
from ctypes import *

from asciimatics.effects import Print, Snow, Wipe
from asciimatics.renderers import ImageFile
from asciimatics.scene import Scene
from asciimatics.screen import Screen, KeyboardEvent, StopApplication

from TUI.__main__ import SaveSystem


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

    screen.print_at(u'Нажмите "X", чтобы вернуться в меню . . .', screen.width // 2 - 20, screen.height // 2 - 5, Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(2)
    screen.clear()

    effects = [
        Print(
            screen,
            ImageFile(f"{SaveSystem.CWD}/data/lose.jpg", height=20),
            screen.height // 2 - 10),
        Snow(screen),
        Wipe(screen)
    ]

    screen.play([Scene(effects, 500)], unhandled_input=stop_key)


if __name__ == '__main__':
    x = (windll.user32.GetSystemMetrics(0)) // 5
    y = (windll.user32.GetSystemMetrics(1)) // 5
    os.system('mode con cols=' + str(x) + ' lines=' + str(y))

    Screen.wrapper(main_scr)
