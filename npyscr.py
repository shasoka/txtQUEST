# -*- coding: utf-8 -*-

"""
Модуль с интерфейсом для TxtRPG.
"""

import json
import npyscreen
import curses
import os
import main_hero_class
from ctypes import *
from game import map_of_world, description_output


class App(npyscreen.StandardApp):
    """
    Класс приложения.
    """

    def onStart(self):
        """
        Метод, свзяывающий форму с приложением.
        """

        self.addForm("MAIN", MainForm, name=" Х Р А М ")


class DefaultTheme(npyscreen.ThemeManager):
    """
    Класс ч/б темы.
    """

    default_colors = {
        'DEFAULT': 'WHITE_BLACK',
        'FORMDEFAULT': 'WHITE_BLACK',
        'NO_EDIT': 'WHITE_BLACK',
        'STANDOUT': 'WHITE_BLACK',
        'CURSOR': 'WHITE_BLACK',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL': 'WHITE_BLACK',
        'LABELBOLD': 'WHITE_BLACK',
        'CONTROL': 'YELLOW_BLACK',
        'WARNING': 'YELLOW_BLACK',
        'CRITICAL': 'RED_BLACK',
        'GOOD': 'GREEN_BLACK',
        'GOODHL': 'GREEN_BLACK',
        'VERYGOOD': 'GREEN_BLACK',
        'CAUTION': 'WHITE_YELLOW',
        'CAUTIONHL': 'WHITE_BLACK',
    }


class Speaker(npyscreen.BoxTitle):
    """
    Основное окно вывода текста.
    """

    _contained_widget = npyscreen.MultiLineEdit


class Inventory(npyscreen.BoxTitle):
    """
    Правый блок инвентаря.
    """

    _contained_widget = npyscreen.SelectOne


class MainForm(npyscreen.FormBaseNewWithMenus):
    """
    Класс основной формы.
    """

    frame = 0
    hero = main_hero_class.MainHero()

    with open("intro.json", "r") as file:
        full_intro = json.load(file)

    def __init__(self, name=None, parentApp=None, framed=None, help=None,  # Добавить хелп
                 color='FORMDEFAULT', widget_list=None, cycle_widgets=False,
                 *args, **keywords):
        super().__init__(name, parentApp, framed, help, color, widget_list,
                         cycle_widgets, args, keywords)

    def draw_form(self):
        """
        Метод, отрисовывающий меню по ^X.
        """

        super(npyscreen.FormBaseNewWithMenus, self).draw_form()
        menu_advert = " " + self.__class__.MENU_KEY + ": М Е Н Ю "
        if isinstance(menu_advert, bytes):
            menu_advert = menu_advert.decode('utf-8', 'replace')
        yd, xd = self.display_menu_advert_at()
        self.add_line(yd, xd,
                      menu_advert,
                      self.make_attributes_list(menu_advert, curses.A_NORMAL),
                      self.columns - xd - 1
                      )

    def create(self):
        """
        Метод, отрисовывающий всю форму.
        """

        npyscreen.setTheme(DefaultTheme)

        y, x = self.useable_space()

        storytelling = self.text_for_storytel(self.full_intro[self.frame])

        self.main_menu = self.new_menu(name=' М Е Н Ю ')
        self.main_menu.addItem(text=' СОХРАНИТЬ И ВЫЙТИ',
                               onSelect=self.main_menu_save_exit)
        self.main_menu.addItem(text=' ВЫЙТИ', onSelect=self.main_menu_exit)

        self.speaker = self.add(Speaker, editable=False, max_height=y//2+1,
                                rely=1, value=storytelling)

        self.action_1 = self.add(npyscreen.ButtonPress, max_width=x//2-5,
                                 rely=y//2+2, name='В П Е Р Е Д',
                                 when_pressed_function=
                                 self.prologue_next_frame)
        self.action_2 = self.add(npyscreen.ButtonPress, max_width=x//2-5,
                                 rely=y//2+3, name='Н А З А Д  ',
                                 when_pressed_function=
                                 self.prologue_previous_frame)
        self.action_3 = self.add(npyscreen.ButtonPress, max_width=x//2-5,
                                 rely=y//2+4, name='           ',
                                 when_pressed_function=self.move_right,
                                 editable=False)
        self.action_4 = self.add(npyscreen.ButtonPress, max_width=x//2-5,
                                 rely=y//2+5, name='           ',
                                 when_pressed_function=self.move_left,
                                 editable=False)

        slots_loc = ['[ П У С Т О ]',
                     '[ П У С Т О ]',
                     '[ П У С Т О ]']
        self.loc_items = self.add(Inventory, editable=True,
                                  name=' Н А Й Д Е Н О ', rely=y//2+2,
                                  relx=2*x//4, max_width=x//4 - 2,
                                  max_height=y//2-10, values=slots_loc)

        slots_inv = ['[ П У С Т О ]',
                     '[ П У С Т О ]',
                     '[ П У С Т О ]']
        self.inventory = self.add(Inventory, editable=True,
                                  name=' И Н В Е Н Т А Р Ь ', rely=y//2+2,
                                  relx=3*x//4, max_height=y//2-10,
                                  values=slots_inv)

        self.add(npyscreen.ButtonPress, rely=y-8, relx=x//2+6,
                 name='П О Д О Б Р А Т Ь')
        self.add(npyscreen.ButtonPress, rely=y-8, relx=x-31,
                 name='И С П О Л Ь З О В А Т Ь')

        self.mind = self.add(npyscreen.Slider, editable=False, value=100,
                             step=1, block_color='CAUTIONHL', rely=y-5)

        self.add(npyscreen.Textfield, value='ШКАЛА РАССУДКА', rely=y-7,
                 editable=False)
        self.add(npyscreen.Textfield, value='(build 1.2b)', rely=y-3,
                 editable=False)

    def prologue_next_frame(self):
        """
        Вывод следующего кадра.
        """

        if self.frame < 4:
            self.frame += 1
            storytelling = self.text_for_storytel(self.full_intro[self.frame])
            self.speaker.value = storytelling
            self.speaker.display()

        elif self.frame == 4:

            message_to_display = 'Вы входите в таинственный ХРАМ.\nЧт@ жд@т ' \
                                 'вас в#утри?.,.\n|\n|\n|\n|\nНажмите ENTER,' \
                                 ' чтобы продолжить.'
            npyscreen.notify_confirm(message_to_display,
                                     title='', editw=1,
                                     form_color='CRITICAL')

            self.speaker.value = \
                self.text_for_storytel(map_of_world
                                       [self.hero.coordinates[0]]
                                       [self.hero.coordinates[1] - 1]['map'])
            self.speaker.display()

            self.action_1.when_pressed_function = self.move_forward
            self.action_2.when_pressed_function = self.move_back
            self.action_3.name = 'В П Р А В О'
            self.action_3.editable = True
            self.action_4.name = 'В Л Е В О  '
            self.action_4.editable = True

            self.action_1.display()
            self.action_2.display()
            self.action_3.display()
            self.action_4.display()

    def prologue_previous_frame(self):
        """
        Вывод предыдущего кадра.
        """

        if self.frame > 0:
            self.frame -= 1
            storytelling = self.text_for_storytel(self.full_intro[self.frame])
            self.speaker.value = storytelling
            self.speaker.display()
        else:
            pass

    def move_forward(self):
        """
        Движение вне пролога вперед.
        """

        self.hero.move('up')
        self.speaker.value = self.text_for_storytel(description_output
                                                    (self.hero.coordinates,
                                                     self.hero.mind))
        self.speaker.display()

        self.mind.value = self.hero.mind
        self.mind.display()

        if self.hero.coordinates[1] == 9:
            message_to_display = 'Вы уперлись в стену...\n|\n|\n|\n|\n' \
                                 'Для продолжения нажмите ENTER.'
            npyscreen.notify_confirm(message_to_display,
                                     title='', editw=1,
                                     form_color='WARNING')

    def move_back(self):
        """
        Движение вне пролога назад.
        """

        self.hero.move('down')
        self.speaker.value = self.text_for_storytel(
            description_output(self.hero.coordinates, self.hero.mind))
        self.speaker.display()

        self.mind.value = self.hero.mind
        self.mind.display()

        if self.hero.coordinates[1] == -1:
            message_to_display = 'Вы уперлись в стену...\n|\n|\n|\n|\n' \
                                 'Для продолжения нажмите ENTER.'
            npyscreen.notify_confirm(message_to_display,
                                     title='', editw=1,
                                     form_color='WARNING')

    def move_right(self):
        """
        Движение вне пролога вправо.
        """

        self.hero.move('right')
        self.speaker.value = self.text_for_storytel(description_output(self.hero.coordinates, self.hero.mind))
        self.speaker.display()

        self.mind.value = self.hero.mind
        self.mind.display()

        if self.hero.coordinates[0] == 9:
            message_to_display = 'Вы уперлись в стену...\n|\n|\n|\n|\n' \
                                 'Для продолжения нажмите ENTER.'
            npyscreen.notify_confirm(message_to_display,
                                     title='', editw=1,
                                     form_color='WARNING')

    def move_left(self):
        """
        Движение вне пролога влево.
        """

        self.hero.move('left')
        self.speaker.value = self.text_for_storytel(
            description_output(self.hero.coordinates, self.hero.mind))
        self.speaker.display()

        self.mind.value = self.hero.mind
        self.mind.display()

        if self.hero.coordinates[0] == 0:
            message_to_display = 'Вы уперлись в стену...\n|\n|\n|\n|\n' \
                                 'Для продолжения нажмите ENTER.'
            npyscreen.notify_confirm(message_to_display,
                                     title='', editw=1,
                                     form_color='WARNING')

    @staticmethod
    def text_for_storytel(paragraph):
        """
        Возвращает подготовленную к выводу в MultiLineEdit строку.
        """

        k = 0
        for i in range(len(paragraph)):
            k += 1
            if paragraph[i] == '\n':
                k = 0
            if paragraph[i] == ' ':
                for j in range(i + 1, len(paragraph)):
                    if paragraph[j] == ' ':
                        if j - i - 1 + k <= 128:
                            break
                        else:
                            paragraph = paragraph[:i] + '\n' + \
                                        paragraph[i + 1:]
                            k = 0
                            break
        return paragraph

    @staticmethod
    def main_menu_exit():
        """
        Выход по кнопке из меню.
        """

        exit(0)

    @staticmethod
    def main_menu_save_exit():
        """
        Выход с сохранением по кнопке из меню.
        """

        pass


if __name__ == '__main__':
    windll.kernel32.SetConsoleTitleW("XPAM")

    window_x = (windll.user32.GetSystemMetrics(0)) // 5
    window_y = (windll.user32.GetSystemMetrics(1)) // 5
    os.system('mode con cols=' + str(window_x) + ' lines=' + str(window_y))

    MyApp = App()
    MyApp.run()
