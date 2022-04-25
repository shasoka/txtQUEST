import time
from asciimatics.renderers import ImageFile
from asciimatics.screen import Screen, KeyboardEvent, StopApplication
from asciimatics.scene import Scene
from asciimatics.effects import Print, Snow, Wipe, Stars
import os
from ctypes import *


def stop_key(event):
    if isinstance(event, KeyboardEvent):
        c = event.key_code
        if c in (ord("X"), ord("x"), ord("ч"), ord("Ч")):
            raise StopApplication("Intro closed")


def main_scr(screen):
    screen.set_title('XPAM')
    screen.height = 40
    screen.width = 137

    screen.print_at(u'По мотивам книги "Храм" Говарда Лавкрафта . . .',
                    screen.width // 2 - 23, screen.height // 2 - 5,
                    Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(3)
    screen.clear()

    screen.print_at(u'Нажмите "X", чтобы продолжить . . .',
                    screen.width // 2 - 17, screen.height // 2 - 5,
                    Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(1.5)

    effects = [
        Print(
            screen,
            ImageFile("intro.jpg", height=40),
            screen.height // 2 - 20),
        Wipe(screen),
        Snow(screen),
        Stars(screen, count=100)
    ]

    screen.play([Scene(effects, 500)], unhandled_input=stop_key)


if __name__ == '__main__':
    x = (windll.user32.GetSystemMetrics(0)) // 5
    y = (windll.user32.GetSystemMetrics(1)) // 5
    os.system('mode con cols=' + str(x) + ' lines=' + str(y))

    Screen.wrapper(main_scr)
