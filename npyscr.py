# -*- coding: utf-8 -*-

"""
Модуль с интерфейсом для TxtRPG.
"""
import json

import npyscreen
import curses
import os
from ctypes import *


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
        'CONTROL': 'WHITE_BLACK',
        'WARNING': 'WHITE_BLACK',
        'CRITICAL': 'WHITE_BLACK',
        'GOOD': 'WHITE_BLACK',
        'GOODHL': 'WHITE_BLACK',
        'VERYGOOD': 'WHITE_BLACK',
        'CAUTION': 'WHITE_BLACK',
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

        self.speaker = self.add(Speaker, editable=False, max_height=y // 2 + 1,
                                rely=1, value=storytelling)

        self.action_1 = self.add(npyscreen.ButtonPress, max_width=x // 2 - 5,
                                 rely=y // 2 + 2, name='Д А Л Е Е . . .',
                                 when_pressed_function=self.next_frame)
        self.action_2 = self.add(npyscreen.ButtonPress, max_width=x // 2 - 5,
                                 rely=y // 2 + 3, name='Н А З А Д . . .',
                                 when_pressed_function=self.previous_frame)

        slots_inv = ['[ П У С Т О Й  С Л О Т ]',
                     '[ П У С Т О Й  С Л О Т ]',
                     '[ П У С Т О Й  С Л О Т ]']

        self.inventory = self.add(Inventory, editable=True,
                                  name=' И Н В Е Н Т А Р Ь ', rely=y // 2 + 2,
                                  relx=x // 2, max_height=y // 2 - 5, values=slots_inv)

        self.add(npyscreen.ButtonPress, rely=y - 3, relx=x // 2,
                 name='И С П О Л Ь З О В А Т Ь')
        self.add(npyscreen.Textfield, value='-:-', rely=y - 3, relx=x // 2 + 34,
                 editable=False)
        self.add(npyscreen.ButtonPress, rely=y - 3, relx=x - 24,
                 name='О  П Р Е Д М Е Т Е')

        self.add(npyscreen.Textfield, value='(build 1.1b)', rely=y - 3,
                 editable=False)

    def actionSelected(self, act_on_these, key_press):
        pass

    def next_frame(self):
        """
        Вывод следующего кадра.
        """

        if self.frame < 4:
            self.frame += 1
            storytelling = self.text_for_storytel(self.full_intro[self.frame])
            self.speaker.value = storytelling
            self.speaker.display()
        else:
            pass

    def previous_frame(self):
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
