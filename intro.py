import time
from asciimatics.renderers import FigletText
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Cycle, Snow


def main_scr(screen):
    screen.set_title('XPAM')

    screen.print_at(u'Нажмите "q" / "Q", чтобы продолжить . . .', 75, 20,
                    Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()

    time.sleep(2)

    screen.clear()

    screen.print_at(u'По мотивам книги "Храм" Говарда Лавкрафта . . .', 75, 20,
                    Screen.COLOUR_WHITE, Screen.A_BOLD)
    screen.refresh()
    time.sleep(3)

    effects = [
        Cycle(
            screen,
            FigletText("X  P  A  M", font='big'),
            screen.height // 2 - 8),
        Snow(screen)
    ]

    screen.play([Scene(effects, 500)])


Screen.wrapper(main_scr)
