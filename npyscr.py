# -*- coding: utf-8 -*-

import npyscreen
import curses
import os
from ctypes import *


class App(npyscreen.StandardApp):
    def onStart(self):
        self.addForm("MAIN", MainForm, name=" Х Р А М ")


class DefaultTheme(npyscreen.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'WHITE_BLACK',
        'FORMDEFAULT' : 'WHITE_BLACK',
        'NO_EDIT'     : 'WHITE_BLACK',
        'STANDOUT'    : 'WHITE_BLACK',
        'CURSOR'      : 'WHITE_BLACK',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL'       : 'WHITE_BLACK',
        'LABELBOLD'   : 'WHITE_BLACK',
        'CONTROL'     : 'WHITE_BLACK',
        'WARNING'     : 'WHITE_BLACK',
        'CRITICAL'    : 'WHITE_BLACK',
        'GOOD'        : 'WHITE_BLACK',
        'GOODHL'      : 'WHITE_BLACK',
        'VERYGOOD'    : 'WHITE_BLACK',
        'CAUTION'     : 'WHITE_BLACK',
        'CAUTIONHL'   : 'WHITE_BLACK',
    }


class Speaker(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit


class Inventory(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLine


class MainForm(npyscreen.FormBaseNewWithMenus):

    def __init__(self, name=None, parentApp=None, framed=None, help=None,
                 color='FORMDEFAULT',
                 widget_list=None, cycle_widgets=False, *args, **keywords):
        super().__init__(name, parentApp, framed, help, color, widget_list,
                         cycle_widgets, args, keywords)
        self.main_menu = None
        self.speaker = None
        self.actions = None
        self.inventory = None

    def draw_form(self):
        super(npyscreen.FormBaseNewWithMenus, self).draw_form()
        menu_advert = " " + self.__class__.MENU_KEY + ": М Е Н Ю "
        if isinstance(menu_advert, bytes):
            menu_advert = menu_advert.decode('utf-8', 'replace')
        y, x = self.display_menu_advert_at()
        self.add_line(y, x,
                      menu_advert,
                      self.make_attributes_list(menu_advert, curses.A_NORMAL),
                      self.columns - x - 1
                      )

    def create(self):
        npyscreen.setTheme(DefaultTheme)

        y, x = self.useable_space()

        slots_action = ["1. ...", "2. ...", "3. ..."]
        slots_inv = ['1. ФОНАРЬ', '2. ...']
        storytelling = self.text_for_storytel()

        self.main_menu = self.new_menu(name=' М Е Н Ю ')
        self.main_menu.addItem(text=' СОХРАНИТЬ И ВЫЙТИ', onSelect=self.main_menu_save_exit)
        self.main_menu.addItem(text=' ВЫЙТИ', onSelect=self.main_menu_exit)

        self.speaker = self.add(Speaker, editable=False, max_height=y//2+1, rely=1, value=storytelling)

        self.actions = self.add(npyscreen.SelectOne, editable=True, max_width=x//2-5, rely=y//2+2, values=slots_action)

        self.inventory = self.add(Inventory, editable=True, name=' И Н В Е Н Т А Р Ь ', rely=y//2+2, relx=x//2, values=slots_inv)

        # slots = ['+']  # Обновление checkbox'а
        # self.Inventory.display()
        # self.Inventory = self.add(npyscreen.TitleSelectOne, editable=True,
        #                           max_width=x // 2 - 5, rely=27, values=slots,
        #                           name=" М Е Н Ю ")

    # def event_value_edited(self, event):  # Очистка спикера
    #     self.InputBox2.value = self.InputBox1.value
    #     self.InputBox2.display()

    @staticmethod
    def text_for_storytel():
        paragraph = 'Двадцатого августа 1917 года я, Карл-Хайнрих, граф фон Альтберг-Эренштейн, командор-лейтенант имперского военного флота, передаю эту бутылку и записи Атлантическому океану в месте, неизвестном мне: вероятно, это 20 градусов северной широты и 35 градусов восточной долготы, где мой корабль беспомощно лежит на океанском дне. Поступаю так в силу моего желания предать гласности некоторые необычные факты: нет вероятности, что я выживу и смогу рассказать об этом сам, потому что окружающие обстоятельства настолько же необычайны, насколько угрожающи, и включают в себя не только безнадежное повреждение У-29, но и совершенно разрушительное ослабление моей немецкой железной воли.'
        l = 0
        for i in range(len(paragraph)):
            l += 1
            if paragraph[i] == ' ':
                for j in range(i+1, len(paragraph)):
                    if paragraph[j] == ' ':
                        if j - i - 1 + l <= 128:
                            break
                        else:
                            paragraph = paragraph[:i] + '\n' + paragraph[i + 1:]
                            l = 0
                            break
        return paragraph

    @staticmethod
    def main_menu_exit():
        exit(0)

    @staticmethod
    def main_menu_save_exit():
        pass


if __name__ == '__main__':

    windll.kernel32.SetConsoleTitleW("XPAM")

    x = (windll.user32.GetSystemMetrics(0)) // 5
    y = (windll.user32.GetSystemMetrics(1)) // 5
    os.system('mode con cols=' + str(x) + ' lines=' + str(y))

    MyApp = App()
    MyApp.run()
