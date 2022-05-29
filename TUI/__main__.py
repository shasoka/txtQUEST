# -*- coding: utf-8 -*-

"""
TUI для TxtRPG Храм.
Точка входа всего проекта.
"""

import curses
import datetime
import json
import os
import pickle
import random
import subprocess
import sys
import time
from ctypes import *

import keyboard
import mouse
import npyscreen
import py_win_keyboard_layout

from TUI import main_hero_class as main_hero_class
from TUI import quests as quests
from TUI.map_output import load_map as load_map
from TUI.map_output import description_output as description_output
from TUI.words import word_guess as word_guess
from TUI.words import word_make as word_make


class App(npyscreen.StandardApp):
    """
    Класс приложения.
    """

    def onStart(self):
        """
        Метод, свзяывающий форму с приложением.
        """

        self.addForm('MAIN', WelcomeForm, name=' Х Р А М ')
        self.registerForm('welcomeMenu', WelcomeForm())


class MapLoaderThread:
    """
    Класс параллельного процесса генерации карты.
    """

    CURRENT_PROCCESS = None
    TIMER = None

    @classmethod
    def new_proccess(cls):
        """
        Метод, запускающий новый процесс.
        """

        cls.CURRENT_PROCCESS = subprocess.Popen([sys.executable, f'{SaveSystem.CWD[:-4]}/MAP/map_generator.py'])
        cls.TIMER = time.time()

    @classmethod
    def check_status(cls):
        """
        Метод, проверяющий текущее состояние процесса.
        :return: 0 в случае успешной генерации, None в случае, если генерация не завершена
        """

        if cls.CURRENT_PROCCESS:
            return cls.CURRENT_PROCCESS.poll()
        else:
            return 0

    @classmethod
    def kill_proccess(cls):
        """
        Метод, удаляющий процесс из ОЗУ.
        """

        if cls.CURRENT_PROCCESS:
            cls.CURRENT_PROCCESS.kill()
            cls.CURRENT_PROCCESS = None
            cls.TIMER = None


class SaveSystem:
    """
    Класс, содержащий переменные, которые необходимо передавать между формами.
    - Создает файл для сохранения
    - Создает сейв
    - Удаляет сейв в случае ненадобности
    """

    CWD = str(os.path.abspath(__file__))[:-12]
    f_name = None
    new_save = False
    loaded_data = None

    @classmethod
    def create_fname(cls):
        """
        Метод, создающий пустой файл для будущего сохранения.
        """

        cls.new_save = True
        cls.f_name = 'SAVE ' + str(datetime.datetime.now())[:-7].replace(':', '-', 3) + '.dat'

    @classmethod
    def save_existing(cls, data: dict):
        """
        Сохранение в имеющийся файл.
        """

        with open(fr'{SaveSystem.CWD}/saves/{cls.f_name}', 'wb') as f:
            pickle.dump(data, f)
        cls.f_name = None
        if cls.new_save:
            cls.new_save = False

    @classmethod
    def delete_save(cls):
        """
        Удаление файла в случае не сохранения новой игры.
        """

        if not cls.new_save:
            os.remove(fr'{SaveSystem.CWD}/saves/{cls.f_name}')
            cls.f_name = None
            cls.new_save = False

    @classmethod
    def load(cls, f_name):
        """
        Загрузчик сохранения из файла.
        """

        cls.f_name = f_name + '.dat'
        cls.new_save = False
        with open(fr'{SaveSystem.CWD}/saves/{cls.f_name}', 'rb') as f:
            cls.loaded_data = pickle.load(f)


class Picker(npyscreen.BoxTitle):
    """
    Виджет с SelectOne внутри.
    """

    _contained_widget = npyscreen.SelectOne

    @staticmethod
    def highlight_on_top():
        """
        Функция, поднимающая выделение строки в списке наверх.
        """

        keyboard.send('ctrl+shift')
        [keyboard.send('k') for _ in range(4)]
        keyboard.send('ctrl+shift')

    @staticmethod
    def saves_updater():
        """
        Метод, состовляющий список сохранений
        """

        saves = sorted(os.listdir(f'{SaveSystem.CWD}/saves'), reverse=True)
        saves.pop(len(saves) - 1)
        i = 0
        while i < 5:
            if i < len(saves):
                saves[i] = saves[i][:-4]
            else:
                saves.append('   [ П У С Т О ]        ')
            i += 1
        return saves


class Speaker(npyscreen.BoxTitle):
    """
    Виджет для вывода текста.
    """

    _contained_widget = npyscreen.MultiLineEdit

    @staticmethod
    def text_for_storytel(paragraph, max_len):
        """
        Возвращает подготовленную к выводу в MultiLineEdit строку.
        """
        # Ширина консольного окна - 137. Символов в игровом спикере - 127, в квестовом - 27. С каждого края - 9/2.

        k = 0
        for i in range(len(paragraph)):
            k += 1
            if paragraph[i] == '\n':
                k = 0
            if paragraph[i] == ' ':
                for j in range(i + 1, len(paragraph)):
                    if paragraph[j] == ' ':
                        if j - i - 1 + k <= max_len:
                            break
                        else:
                            paragraph = paragraph[:i] + '\n' + paragraph[i + 1:]
                            k = 0
                            break
        return paragraph


class WelcomeForm(npyscreen.FormBaseNew):
    """
    Класс основной формы.
    """

    with open(f'{SaveSystem.CWD}/data/helpstr.json', 'r') as file:
        helpstr = json.load(file)

    def __init__(self, name=' Х Р А М ', parentApp=App, framed=None,
                 help=helpstr,
                 color='FORMDEFAULT', widget_list=None, cycle_widgets=False,
                 *args, **keywords):
        super().__init__(name, parentApp, framed, help, color, widget_list, cycle_widgets, args, keywords)

        self.NEW_GAME_FLAG = 0  # На случай открытия справки при входе в новую игру
        self.WAIT_AGREEMENT = 0  # На случай подтверждения ожидания генерации
        self.handlers.pop("^O")
        self.handlers.pop("^L")

        npyscreen.fmPopup.Popup.SHOW_ATX = npyscreen.fmPopup.ActionPopup.SHOW_ATX = (self.useable_space()[1] - 58 - 9 // 2) // 2  # Определение координат для всплывающих окон
        npyscreen.fmPopup.Popup.SHOW_ATY = npyscreen.fmPopup.ActionPopup.SHOW_ATY = (self.useable_space()[0] - 12 - 9 // 2) // 2

    def draw_title_and_help(self):
        """
        Метод, отрисовывающий надпись меню в правой верхней части экрана.
        """

        _title = self.name[:(self.columns - 4)]
        _title = ' ' + str(_title) + ' '
        self.add_line(0, 1,
                      _title,
                      self.make_attributes_list(_title, curses.A_NORMAL),
                      self.columns - 4
                      )

        help_advert = " F1: О  И Г Р Е "
        self.add_line(
            0, self.curses_pad.getmaxyx()[1] - len(help_advert) - 2,
            help_advert,
            self.make_attributes_list(help_advert, curses.A_NORMAL),
            len(help_advert)
        )

    def h_display_help(self, input):
        """
        Метод, отрисовывающий окно Help.
        """

        if self.help is None:
            return
        if self.name:
            help_name = "%s Справка" % self.name
        else:
            help_name = None
        curses.flushinp()
        npyscreen.util_viewhelp.view_help(self.help, title=help_name, autowrap=self.WRAP_HELP)
        self.display()
        return True

    def create(self):
        """
        Метод, отрисовывающий всю форму.
        """

        y, x = self.useable_space()

        saves = Picker.saves_updater()

        self.action_new_game = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 - 3, name='    Н О В А Я  И Г Р А      ', when_pressed_function=self.new_game)
        self.action_load_game = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 - 2, name=' З А Г Р У З И Т Ь  И Г Р У ', when_pressed_function=self.load_btn)
        self.action_exit = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 - 1, name='         В Ы Х О Д          ', when_pressed_function=self.exit)
        self.saves_picker = self.add(Picker, rely=y // 2, relx=(x - 29 - 9 // 2) // 2, max_width=34, max_height=y // 2 - 12, values=saves, editable=False, hidden=True, scroll_exit=True)
        self.action_confirm_selection = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 + 8, name=28 * ' ', editable=False, when_pressed_function=(lambda: self.enter_from_save(self.saves_picker.value)))
        self.action_delete_selection = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 + 9, name=28 * ' ', editable=False, when_pressed_function=(lambda: self.delete_save(self.saves_picker.value)))
        self.action_cancel_selection = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 + 10, name=28 * ' ', editable=False, when_pressed_function=self.cancel)

        self.add(npyscreen.Textfield, value='(release v1.0)', rely=y - 3, editable=False)

    def new_game(self):
        """
        Начать новую игру.
        """

        if self.NEW_GAME_FLAG:  # Если была выведена справка
            if MapLoaderThread.check_status() is not None:  # Если процесс генерации уже завершен
                MapLoaderThread.kill_proccess()  # Рестартим процесс для следующей сессии
                MapLoaderThread.new_proccess()
            # Иначе даем текущему процессу завершиться
            SaveSystem.create_fname()
            self.parentApp.registerForm('inGame', GameForm())
            self.parentApp.switchForm('inGame')
            self.parentApp.removeForm('welcomeMenu')
            return

        if len(os.listdir(f'{SaveSystem.CWD}/saves')) < 6 and not self.NEW_GAME_FLAG:
            if MapLoaderThread.check_status() is None:  # Если процесс генерации не завершен
                if (time_left := 34 - int((time.time() - MapLoaderThread.TIMER))) < 0:
                    time_left = 0
                msg = f'В данный момент происходит генерация новой карты.\nОсталось примерно {time_left} секунд . . . \nЕсли желаете начать игру с новой картой, попробуйте войти через несколько секунд.\nИначе новая игра начнется с прежней картой.\n|\n|\nОжидать?'
                npyscreen.utilNotify.YesNoPopup.OK_BUTTON_TEXT = 'Нет'
                npyscreen.utilNotify.YesNoPopup.CANCEL_BUTTON_TEXT = 'Да'
                if npyscreen.notify_yes_no(msg, title=' ГЕНЕРАЦИЯ КАРТЫ ', editw=1, form_color='STANDOUT'):
                    msg = 'Вы начинаете новую игру. Карта сгенерирована.\nРекомендуем ознакомиться с краткой справкой (F1) перед началом.\nОткрыть справку?'
                    if npyscreen.notify_yes_no(msg, title=' НОВОЕ НАЧАЛО... ', editw=1, form_color='STANDOUT'):
                        SaveSystem.create_fname()
                        GameForm.map_of_world = load_map()  # Загрузка актуальной версии карты
                        self.parentApp.registerForm('inGame', GameForm())
                        self.parentApp.switchForm('inGame')
                        self.parentApp.removeForm('welcomeMenu')
                    else:
                        keyboard.send('F1')
                        self.NEW_GAME_FLAG = 1
                        self.action_new_game.name = '    П Р О Д О Л Ж И Т Ь     '
                        self.action_new_game.display()
                else:  # Ожидание
                    return
            else:  # Если процесс генерации завершен
                msg = 'Вы начинаете новую игру. Карта сгенерирована.\nРекомендуем ознакомиться с краткой справкой (F1) перед началом.\nОткрыть справку?'
                npyscreen.utilNotify.YesNoPopup.OK_BUTTON_TEXT = 'Нет'
                npyscreen.utilNotify.YesNoPopup.CANCEL_BUTTON_TEXT = 'Да'
                if npyscreen.notify_yes_no(msg, title=' НОВОЕ НАЧАЛО... ', editw=1, form_color='STANDOUT'):
                    MapLoaderThread.new_proccess()  # Запускаем новый процесс генерации для следующей сессии
                    SaveSystem.create_fname()
                    GameForm.map_of_world = load_map()  # Загрузка актуальной версии карты
                    self.parentApp.registerForm('inGame', GameForm())
                    self.parentApp.switchForm('inGame')
                    self.parentApp.removeForm('welcomeMenu')
                else:
                    keyboard.send('F1')
                    self.NEW_GAME_FLAG = 1
                    self.action_new_game.name = '    П Р О Д О Л Ж И Т Ь     '
                    self.action_new_game.display()
        else:
            msg = 'Допускается создание не более 5-ти сохранений игры.\nДостигнуто максимальное число сохранений\nВойдите в существующую игру или удалите одно из прошлых сохранений.\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' ОШИБКА СОХРАНЕНИЯ ', editw=1, form_color='DANGER')

    def load_btn(self):
        """
        Промежуточная кнопка загрузки игры.
        """

        flag = 0
        for i in range(len(self.saves_picker.values)):
            if 'SAVE' in self.saves_picker.values[i]:
                keyboard.send('tab')
                Picker.highlight_on_top()

                self.PREVIOS_BTN_NAME = self.action_new_game.name  # Имя может измениться на ПРОДОЛЖИТЬ
                self.action_new_game.name = 28 * ' '
                self.action_new_game.editable = False
                self.action_new_game.display()

                self.action_exit.name = 28 * ' '
                self.action_exit.editable = False
                self.action_exit.display()

                self.saves_picker.editable = True
                self.saves_picker.hidden = False
                self.saves_picker.display()

                self.action_confirm_selection.editable = True
                self.action_confirm_selection.name = '         В О Й Т И          '
                self.action_confirm_selection.display()

                self.action_delete_selection.editable = True
                self.action_delete_selection.name = '       У Д А Л И Т Ь        '
                self.action_delete_selection.display()

                self.action_cancel_selection.editable = True
                self.action_cancel_selection.name = '         Н А З А Д          '
                self.action_cancel_selection.display()

                self.action_load_game.editable = False
                self.action_load_game.display()

                flag = 1
                break
        if not flag:
            msg = 'У вас пока нет сохранений.\n|\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' СОХРАНЕНИЯ ОТСУТСТВУЮТ ', editw=1, form_color='WARNING')

    def enter_from_save(self, file_to_load):
        """
        Вход в игру из сохранения.
        """

        if not file_to_load:
            msg = 'Выберите одно из сохранений.\n|\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' НИЧЕГО НЕ ВЫБРАНО ', editw=1, form_color='WARNING')
        elif 'SAVE' in self.saves_picker.values[file_to_load[0]]:
            msg = 'Вы собираетесь загрузить сохранение.\nВы уверены?'
            npyscreen.utilNotify.YesNoPopup.OK_BUTTON_TEXT = 'Нет'
            npyscreen.utilNotify.YesNoPopup.CANCEL_BUTTON_TEXT = 'Да'
            if not npyscreen.notify_yes_no(msg, title=' ВХОД В ИГРУ ', editw=1, form_color='STANDOUT'):
                SaveSystem.load(self.saves_picker.values[file_to_load[0]])
                self.parentApp.registerForm('inGame', GameForm())
                self.parentApp.switchForm('inGame')
                self.parentApp.removeForm('welcomeMenu')
        else:
            msg = 'Этот слот пуст!\n|\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' СОХРАНЕНИЕ ОТСУТСТВУЕТ ', editw=1, form_color='WARNING')

    def delete_save(self, file_to_delete):
        """
        Функция для кнопки удаления сохранения.
        """

        if not file_to_delete:
            msg = 'Выберите одно из сохранений.\n|\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' НИЧЕГО НЕ ВЫБРАНО ', editw=1, form_color='WARNING')
        elif 'SAVE' in self.saves_picker.values[file_to_delete[0]]:
            msg = 'Вы собираетесь удалить сохранение.\nВы уверены?'
            npyscreen.utilNotify.YesNoPopup.OK_BUTTON_TEXT = 'Да'
            npyscreen.utilNotify.YesNoPopup.CANCEL_BUTTON_TEXT = 'Нет'
            if npyscreen.notify_yes_no(msg, title=' УДАЛЕНИЕ СОХРАНЕНИЯ ', editw=1, form_color='DANGER'):
                os.remove(fr'{SaveSystem.CWD}/saves/{self.saves_picker.values[file_to_delete[0]]}.dat')
                saves = Picker.saves_updater()
                self.saves_picker.values = saves
                self.saves_picker.value = []
                self.saves_picker.display()

                [keyboard.send('shift+tab') for _ in range(2)]
                Picker.highlight_on_top()

                flag = 0
                for i in range(len(saves)):
                    if 'SAVE' in saves[i]:
                        flag = 1
                        break
                if not flag:
                    msg = 'Все сохранения удалены.\n|\n|\n|\n|\n|\nНажмите ENTER дважды, чтобы продолжить.'
                    npyscreen.notify_confirm(msg, title=' СОХРАНЕНИЯ ОТСУТСТВУЮТ ', editw=1, form_color='WARNING')
                    self.cancel()

        else:
            msg = 'Этот слот пуст!\n|\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' СОХРАНЕНИЕ ОТСУТСТВУЕТ ', editw=1, form_color='WARNING')

    def cancel(self):
        """
        Функция для отмены загрузки игры.
        """

        self.action_new_game.name = self.PREVIOS_BTN_NAME
        self.action_new_game.editable = True
        self.action_new_game.display()

        self.action_exit.name = '         В Ы Х О Д          '
        self.action_exit.editable = True
        self.action_exit.display()

        self.saves_picker.editable = False
        self.saves_picker.hidden = True
        self.saves_picker.value = []
        self.saves_picker.display()

        self.action_confirm_selection.editable = False
        self.action_confirm_selection.name = 28 * ' '
        self.action_confirm_selection.display()

        self.action_delete_selection.editable = False
        self.action_delete_selection.name = 28 * ' '
        self.action_delete_selection.display()

        self.action_cancel_selection.editable = False
        self.action_cancel_selection.name = 28 * ' '
        self.action_cancel_selection.display()

        self.action_load_game.editable = True
        self.action_load_game.display()

        [keyboard.send('shift+tab') for _ in range(3)]

    @staticmethod
    def exit():
        """
        Выход из приложения.
        """

        MapLoaderThread.kill_proccess()
        exit(0)


class GameForm(npyscreen.FormBaseNewWithMenus):
    """
    Класс основной формы.
    """

    slots_loc_default = ['[ П У С Т О ]']
    slots_inv_default = ['[ П У С Т О ]']  # Дефолтные пустые окна предметов

    slots_alias = {'light': 'Л Ю М Е Н',
                   'figure': 'С Т А Т У Я',
                   'dust': 'П Р А Х'}  # Словарь псевдонимов для игровых предметов

    hero = main_hero_class.MainHero()
    quests_dict = {
        "wall": {
            "text": "На стене виднеются углубления похожие на надпись. Вокруг слишком темно, света не хватает, чтобы разобрать написанное.",
            "quest": "Найдите способ прочесть надпись и вернитесь к резной стене. \nНе заблудитесь в пути...",
            "func": quests.wall_quest_meeting,
            "complete": False},
        "statue": {
            "text": "...едва уцелевший одинокий постамент. Возможно, Вам удастся наконец найти свое спасение!",
            "quest": "Найдите статуэтку и вознесите ее к алтарю.",
            "func": quests.statue_quest_meeting,
            "complete": False},
        "end": {
            "quest": "Ваши муки окончены.\nА может... это было страшным сном?"}
    }

    frame = 0
    LUMEN_FLAG = 0
    DUST_FLAG = 0
    FIGURE_FLAG = 0
    MIND_FLAG = 0

    with open(f"{SaveSystem.CWD}/data/intro.json", "r") as file:
        full_intro = json.load(file)

    def __init__(self, name=' Х Р А М ', parentApp=App, framed=None,
                 help=WelcomeForm.helpstr,
                 color='FORMDEFAULT', widget_list=None, cycle_widgets=False,
                 *args, **keywords):
        super().__init__(name, parentApp, framed, help, color, widget_list, cycle_widgets, args, keywords)

        npyscreen.wgmultiline.MORE_LABEL = '- еще (↓/↑) -'  # Переопределение надписей
        npyscreen.utilNotify.YesNoPopup.OK_BUTTON_TEXT = 'Да'
        npyscreen.utilNotify.YesNoPopup.CANCEL_BUTTON_TEXT = 'Нет'

        npyscreen.fmPopup.Popup.SHOW_ATX = npyscreen.fmPopup.ActionPopup.SHOW_ATX = (self.useable_space()[1] - 60 - 9 // 2) // 2  # Переопределение координат для всплывающих окон
        npyscreen.fmPopup.Popup.SHOW_ATY = npyscreen.fmPopup.ActionPopup.SHOW_ATY = (self.useable_space()[0] // 2 - 12) // 2 + 1

        self.handlers.pop("^O")
        self.handlers.pop("^L")
        self.add_handlers({ord('Ч'): self.prologue_next_frame, ord('ч'): self.prologue_next_frame,
                           ord('Я'): self.prologue_previous_frame, ord('я'): self.prologue_previous_frame})

    def draw_form(self):
        """
        Метод, отрисовывающий надпись меню в левой нижней части экрана.
        """

        super(npyscreen.FormBaseNewWithMenus, self).draw_form()
        menu_advert = " " + self.__class__.MENU_KEY + ": М Е Н Ю "
        yd, xd = self.display_menu_advert_at()
        self.add_line(yd, xd,
                      menu_advert,
                      self.make_attributes_list(menu_advert, curses.A_NORMAL),
                      self.columns - xd - 1
                      )

    def initialize_menus(self):
        """
        Метод, инициализирущий новое меню.
        """

        if self.MENU_WIDTH:
            self._NMDisplay = self.MENU_DISPLAY_TYPE(columns=self.MENU_WIDTH)
        else:
            self._NMDisplay = self.MENU_DISPLAY_TYPE(show_atx=(self.useable_space()[1] - 39 - 9 // 2) // 2, show_aty=(self.useable_space()[0] // 2 - 9) // 2 + 2, lines=9, columns=39)
        if not hasattr(self, '_NMenuList'):
            self._NMenuList = []
        self._MainMenu = npyscreen.muNewMenu.NewMenu
        self.add_handlers({self.__class__.MENU_KEY: self.root_menu})

    def draw_title_and_help(self):
        """
        Метод, отрисовывающий надпись меню в правой верхней части экрана.
        """

        _title = self.name[:(self.columns - 4)]
        _title = ' ' + str(_title) + ' '
        self.add_line(0, 1, _title, self.make_attributes_list(_title, curses.A_NORMAL), self.columns - 4)
        help_advert = " F1: О  И Г Р Е "
        self.add_line(
            0, self.curses_pad.getmaxyx()[1] - len(help_advert) - 2,
            help_advert,
            self.make_attributes_list(help_advert, curses.A_NORMAL),
            len(help_advert)
        )

    def h_display_help(self, input):
        """
        Метод, отрисовывающий окно Help.
        """

        if self.help is None:
            return
        if self.name:
            help_name = "%s Справка " % self.name
        else:
            help_name = None
        curses.flushinp()
        npyscreen.util_viewhelp.view_help(self.help, title=help_name, autowrap=self.WRAP_HELP)
        self.display()
        return True

    def create(self):
        """
        Метод, отрисовывающий всю форму.
        """

        y, x = self.useable_space()

        self.main_menu = self.new_menu(name=' М Е Н Ю |==================| ESC ')
        self.main_menu.addItem(text=' СОХРАНИТЬ И ВЫЙТИ В МЕНЮ  ', onSelect=self.back_to_menu_save)
        self.main_menu.addItem(text=' ВЫЙТИ В МЕНЮ              ', onSelect=self.back_to_menu)
        self.main_menu.addItem(text=' СОХРАНИТЬ И ПОКИНУТЬ ХРАМ ', onSelect=self.exit_save)
        self.main_menu.addItem(text=' ПОКИНУТЬ ХРАМ             ', onSelect=self.exit_no_save)

        Speaker._contained_widget = npyscreen.Textfield  # Изменение виджета спикера для того, чтобы игрок по нажатию Enter падал на кнопку ввода во время головоломки со словами
        self.word_guesser = self.add(Speaker, color='STANDOUT', scroll_exit=True, exit_right=True, exit_left=True, rely=y // 2 + 5, relx=(x - 22) // 2 + 1, max_width=19, max_height=3, name=' ↓ ↓ ↓ ↓ ', hidden=True, editable=False)
        Speaker._contained_widget = npyscreen.MultiLineEdit
        self.action_enter = self.add(npyscreen.ButtonPress, rely=y // 2 + 8, relx=(x - 22) // 2 + 1, name=15 * ' ', editable=False, when_pressed_function=(lambda: self.enter(self.word_and_ans)))
        self.speaker = self.add(Speaker, editable=False, max_height=y // 2 + 1, rely=1)
        self.action_forward = self.add(npyscreen.ButtonPress, rely=y // 2 + 2, name='(X) В П Е Р Е Д')
        self.action_backward = self.add(npyscreen.ButtonPress, rely=y // 2 + 3, name=15 * ' ', editable=False)
        self.action_right = self.add(npyscreen.ButtonPress, rely=y // 2 + 4, name=15 * ' ', editable=False)
        self.action_left = self.add(npyscreen.ButtonPress, rely=y // 2 + 5, name=15 * ' ', editable=False)
        self.quest_bar = self.add(Speaker, color='STANDOUT', scroll_exit=True, exit_right=True, exit_left=True, rely=y // 2 + 2, relx=x // 4, max_width=x // 4 - 2, max_height=y // 2 - 10, editable=False, name=' З А Д А Н И Я ')
        self.loc_items = self.add(Picker, color='STANDOUT', scroll_exit=True, exit_right=True, exit_left=True, editable=False, name=' Н А Й Д Е Н О ', rely=y // 2 + 2, relx=2 * x // 4, max_width=x // 4 - 2, max_height=y // 2 - 10)
        self.action_collect = self.add(npyscreen.ButtonPress, rely=y - 8, relx=2 * x // 4, name=25 * ' ', editable=False, when_pressed_function=self.collect)
        self.inventory = self.add(Picker, color='STANDOUT', scroll_exit=True, exit_right=True, exit_left=True, editable=False, name=' И Н В Е Н Т А Р Ь ', rely=y // 2 + 2, relx=3 * x // 4, max_height=y // 2 - 10, max_width=x // 4 - 2)
        self.action_use = self.add(npyscreen.ButtonPress, rely=y - 8, relx=3 * x // 4 + 2, name=25 * ' ', editable=False, when_pressed_function=self.use)
        self.mind = self.add(npyscreen.Slider, editable=False, lowest=0, step=1, block_color='CAUTIONHL', rely=y - 5)

        self.add(npyscreen.Textfield, value='ШКАЛА РАССУДКА', rely=y - 7, editable=False)
        self.add(npyscreen.Textfield, value='(release v1.0)', rely=y - 3, editable=False)

        if SaveSystem.new_save:  # Шаблон для новой игры
            GameForm.map_of_world = load_map()  # Загрузка актуальной версии карты
            self.speaker.value = Speaker.text_for_storytel(GameForm.full_intro[self.frame], 127)
            self.quest_bar.value = Speaker.text_for_storytel('Задания появятся после прохождения пролога.', 27)
            self.action_forward.when_pressed_function = self.prologue_next_frame
            self.action_backward.when_pressed_function = self.prologue_previous_frame
            self.loc_items.values = GameForm.slots_loc_default
            self.inventory.values = GameForm.slots_inv_default
            self.inventory.footer = ' С Л О Т О В : 0 / 5 '
            self.mind.value = self.hero.mind

        else:  # Данные из сохранения
            self.map_of_world = SaveSystem.loaded_data['map']  # Загрузка карты
            self.hero = SaveSystem.loaded_data['hero']  # Загрузка персонажа
            self.quests_dict = SaveSystem.loaded_data['quests']  # Загрузка слоавря квестов
            self.frame = 5
            self.mind.value = self.hero.mind  # Обновление полосы рассудка
            self.action_forward.when_pressed_function = (lambda eventHadled=None: self.move('up'))
            self.action_backward.when_pressed_function = (lambda eventHandled=None: self.move('down'))
            self.action_left.when_pressed_function = (lambda eventHandled=None: self.move('left'))
            self.action_right.when_pressed_function = (lambda eventHandled=None: self.move('right'))
            self.action_forward.name = '(W) В П Е Р Е Д'
            self.action_right.name = '(D) В П Р А В О'
            self.action_right.editable = True
            self.action_left.name = '(A) В Л Е В О  '
            self.action_left.editable = True
            self.action_backward.name = '(S) Н А З А Д  '
            self.action_backward.editable = True
            self.speaker.value = Speaker.text_for_storytel(description_output(self.hero, self.map_of_world, self.quests_dict), 127)
            self.inventory.values = SaveSystem.loaded_data['inventory'][0]
            self.inventory.footer = SaveSystem.loaded_data['inventory'][1]
            if '×' in self.inventory.values[0]:
                self.action_use.name = ' И С П О Л Ь З О В А Т Ь '
                self.action_use.editable = True
                self.inventory.editable = True
            self.loc_items.values = SaveSystem.loaded_data['finder']
            if '×' in self.loc_items.values[0]:
                self.action_collect.editable = True
                self.action_collect.name = '     П О Д О Б Р А Т Ь   '
                self.loc_items.editable = True
            self.LUMEN_FLAG, self.DUST_FLAG, self.FIGURE_FLAG, self.MIND_FLAG = SaveSystem.loaded_data['flags']

            self.quest_updater()

            self.add_handlers({ord('Ц'): (lambda eventHandled=None: self.move('up')), ord('ц'): (lambda eventHandled=None: self.move('up')),
                               ord('Ы'): (lambda eventHandled=None: self.move('down')), ord('ы'): (lambda eventHandled=None: self.move('down')),
                               ord('Ф'): (lambda eventHandled=None: self.move('left')), ord('ф'): (lambda eventHandled=None: self.move('left')),
                               ord('В'): (lambda eventHandled=None: self.move('right')), ord('в'): (lambda eventHandled=None: self.move('right'))})

    @staticmethod
    def try_free():
        """
        Метод, проверяющий состояние генератора карты и удаляющий его в случае завершения
        """

        if MapLoaderThread.check_status() is not None:
            MapLoaderThread.kill_proccess()

    def prologue_next_frame(self, eventHandled=None):
        """
        Вывод следующего кадра пролога.
        """

        self.try_free()

        if self.frame < 4:

            self.frame += 1
            if self.frame > 0:
                self.action_backward.editable = True
                self.action_backward.name = '(Z) Н А З А Д  '
                self.action_backward.when_pressed_function = self.prologue_previous_frame
                self.action_backward.display()
            self.speaker.value = Speaker.text_for_storytel(GameForm.full_intro[self.frame], 127)
            self.speaker.display()

        elif self.frame == 4:
            self.frame += 1  # Увеличить кадр, чтобы избежать работу функции по бинду

            if SaveSystem.new_save:
                msg = 'Вы входите в таинственный ХРАМ.\nЧт@ жд@т вас в#утри?.,.\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
                npyscreen.notify_confirm(msg, title=' !"##@/..', editw=1, form_color='DANGER')

                msg = 'В одной из комнат ХРАМА Вам предстоит отыскать таинственную статуэтку некоего Божества, чтобы выбраться из оков глубин...\nДля перемещения по комнатам ХРАМА пользуйтесь предложенными кнопками.\nУправление осуществляется стандартными клавишами (TAB / ENTER / SPACE / ESC и W / A / S / D). Вы можете открыть меню нажав CTRL + X.\nСкоро вы очнетесь в одной из сотен комнат внутри ХРАМА...\nНажмите ENTER дважды, чтобы продолжить.'
                npyscreen.notify_confirm(msg, title=' КОНЕЦ ПРОЛОГА ', form_color='WARNING')

            self.speaker.value = Speaker.text_for_storytel(str('    ' + self.map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['map']), 127)
            self.speaker.display()

            self.quest_bar.value = Speaker.text_for_storytel('Продолжайте исследования...', 27)
            self.quest_bar.display()

            self.action_forward.name = '(W) В П Е Р Е Д'
            self.action_forward.when_pressed_function = (lambda eventHadled=None: self.move('up'))
            self.action_backward.name = '(S) Н А З А Д  '
            self.action_backward.when_pressed_function = (lambda eventHandled=None: self.move('down'))
            self.action_left.when_pressed_function = (lambda eventHandled=None: self.move('left'))
            self.action_right.when_pressed_function = (lambda eventHandled=None: self.move('right'))
            self.action_right.name = '(D) В П Р А В О'
            self.action_right.editable = True
            self.action_left.name = '(A) В Л Е В О  '
            self.action_left.editable = True

            self.action_forward.display()
            self.action_backward.display()
            self.action_right.display()
            self.action_left.display()

            self.handlers.update({ord('Ц'): (lambda eventHandled=None: self.move('up')), ord('ц'): (lambda eventHandled=None: self.move('up')),
                                  ord('Ы'): (lambda eventHandled=None: self.move('down')), ord('ы'): (lambda eventHandled=None: self.move('down')),
                                  ord('Ф'): (lambda eventHandled=None: self.move('left')), ord('ф'): (lambda eventHandled=None: self.move('left')),
                                  ord('В'): (lambda eventHandled=None: self.move('right')), ord('в'): (lambda eventHandled=None: self.move('right'))})

    def prologue_previous_frame(self, eventHandled=None):
        """
        Вывод предыдущего кадра пролога.
        """

        self.try_free()

        if 0 < self.frame < 4:
            self.frame -= 1
            if not self.frame:
                keyboard.send('shift+tab')
                self.action_backward.editable = False
                self.action_backward.name = 14 * ' '
                self.action_backward.when_pressed_function = None
                self.action_backward.display()
            self.speaker.value = Speaker.text_for_storytel(GameForm.full_intro[self.frame], 127)
            self.speaker.display()

    def move(self, key_word):
        """
        Движение вне пролога.
        """

        self.try_free()

        self.hero.move(key_word)
        self.speaker.value = Speaker.text_for_storytel(description_output(self.hero, self.map_of_world, self.quests_dict), 127)
        self.speaker.display()

        self.mind.value = self.hero.mind
        self.mind.display()

        if self.mind.value < 30:
            self.lose()
        else:
            if not self.MIND_FLAG and self.mind.value < 100:
                msg = 'При перемещении по ХРАМУ уровень вашего рассудка будет снижаться на 10 единиц с шансом в 10%.\nЧем ниже этот показатель, тем выше шанс, что ваши глаза и уши начнут вас подводить...\nБудьте осторожны!\n|\n|\nДля продолжения нажмите ENTER.'
                npyscreen.notify_confirm(msg, title=' РАССУДОК ', editw=1, form_color='WARNING')
                self.MIND_FLAG = 1

            msg = 'Вы уперлись в СТЕНУ. Не пытайтесь пройти сквозь неё!\nПопытки выбраться за пределы ХРАМА могут плохо сказаться на вашем РАССУДКЕ...\n|\n|\n|\nДля продолжения нажмите ENTER.'
            if key_word == 'up' or key_word == 'down':
                if self.hero.coordinates[1] == 9 and self.hero.mind:
                    npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')

                elif self.hero.coordinates[1] == -1 and self.hero.mind:
                    npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')
            else:
                if not self.hero.coordinates[0] and self.hero.mind:
                    npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')

                elif self.hero.coordinates[0] == 9 and self.hero.mind:
                    npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')

        self.quest_updater()
        self.items_finder()
        self.inventory_updater()

        self.puzzle()

    def quest_updater(self):
        """
        Метод, проверяющий состояние текущего квеста.
        """

        if self.hero.quest in self.quests_dict:
            if self.hero.QUEST_CHANGED:
                msg = 'НОВОЕ СЮЖЕТНОЕ ЗАДАНИЕ.\n|\n|\n|\n|\nДля продолжения нажмите ENTER'
                npyscreen.notify_confirm(msg, title=' СЮЖЕТ ', editw=1, form_color='STANDOUT')
                self.hero.QUEST_CHANGED = False
            self.quest_bar.value = Speaker.text_for_storytel(self.quests_dict[self.hero.quest]['quest'], 27)
            self.quest_bar.display()
        else:
            self.quest_bar.value = Speaker.text_for_storytel('Продолжайте исследования...', 27)
            self.quest_bar.display()

    def items_finder(self):
        """
        Метод обнаружения предметов на локации.
        """

        self.loc_items.value = []
        self.loc_items.values = GameForm.slots_loc_default
        self.loc_items.editable = False
        self.loc_items.display()
        self.action_collect.editable = False
        self.action_collect.name = 25 * ' '
        self.action_collect.display()
        self.loc_items.display()

        self.slots_loc = []  # Список кортежей ('ПРЕДМЕТ', кол-во) для предметов на каждой локации
        for k, v in self.map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['items'].items():
            if v >= 1:
                self.slots_loc.append((k, self.map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['items'][k]))

        if self.slots_loc:
            self.loc_items.values = [(GameForm.slots_alias[self.slots_loc[i][0]] + '  ×' + str(self.slots_loc[i][1])) for i in range(len(self.slots_loc))]
            self.loc_items.editable = True
            self.loc_items.display()

            self.action_collect.editable = True
            self.action_collect.name = '     П О Д О Б Р А Т Ь   '
            self.action_collect.when_pressed_function = self.collect
            self.action_collect.display()

            for i in range(len(self.slots_loc)):
                if self.slots_loc[i][0] == 'light' and not self.LUMEN_FLAG:
                    msg = 'ЛЮМЕН - ваш лучший друг ... хотя нет, знаете, не самый лучший.\nС шансом в 10% при передвижении по ХРАМУ 1 единица ЛЮМЕНА может загадочным образом исчезнуть из вашего инвентаря, однако, наличие этого источника блеклого света гарантирует стабильность вашего РАССУДКА.\nВ инвентаре может уместиться всего 3 экземпляра.\nДля продолжения нажмите ENTER'
                    self.LUMEN_FLAG = 1
                    npyscreen.notify_confirm(msg, title=' НОВЫЙ ПРЕДМЕТ ', editw=1, form_color='GOOD')
                elif self.slots_loc[i][0] == 'figure' and not self.FIGURE_FLAG:
                    msg = 'На своем пути вы нашли манящуюю статуэтку.\nКто знает, может быть она и есть ваше спасение?..\n|\n|\n|\n|\nДля продолжения нажмите ENTER'
                    self.FIGURE_FLAG = 1
                    npyscreen.notify_confirm(msg, title=' НОВЫЙ СЮЖЕТНЫЙ ПРЕДМЕТ ', editw=1, form_color='GOOD')
                elif self.slots_loc[i][0] == 'dust' and not self.DUST_FLAG:
                    msg = 'Черт возьми, что это?...\nВы нашли загадочный сосуд непередаваемого цвета.\nКажется внутри осталась какая-то едва ли сверкающая пыль. Или чей-то прах?..\nМожет быть с ее помощью удастся прочесть ту надпись на стене?\nИспользуйте его по назначению.\nДля продолжения нажмите ENTER'
                    self.DUST_FLAG = 1
                    npyscreen.notify_confirm(msg, title=' СЮЖЕТНЫЙ ПРЕДМЕТ ', editw=1, form_color='GOOD')

    def collect(self):
        """
        Метод, обрабатывающий сбор предметов по кнопке ПОДОБРАТЬ.
        """

        self.try_free()

        if len(self.inventory.values) == 5:
            msg = 'Ваши карманы совсем забились!.\n|\n|\n|\n|\nДля продолжения нажмите ENTER'
            npyscreen.notify_confirm(msg, title=' ИНВЕНТАРЬ ПОЛОН ', editw=1, form_color='DANGER')
        elif self.loc_items.value:
            index = self.loc_items.value[0]  # Получаем индекс выбранного предмета
            collected_item = self.slots_loc[index]  # Получаем кортеж по индексу
            if self.hero.items[collected_item[0]] == 3:  # Максимум по 3 предмета каждого вида
                msg = 'Достигнуто максимальное количество экзмепляров данного предмета.\nПодобрать невозможно.\n|\n|\nДля продолжения нажмите ENTER'
                npyscreen.notify_confirm(msg, title=' ЛИМИТ ПРЕДМЕТОВ ', editw=1, form_color='DANGER')
            else:
                self.hero.items[collected_item[0]] += collected_item[1]  # Изменение атрибута персонажа
                if self.inventory.values == GameForm.slots_inv_default:  # Если инвентарь пустой
                    self.inventory.values = [GameForm.slots_alias[collected_item[0]] + '  ×' + str(collected_item[1])]
                    self.inventory.footer = f' С Л О Т О В : {len(self.inventory.values)} / 5 '
                else:
                    stacked = False
                    for i in range(len(self.inventory.values)):  # Проверка, есть ли уже такой предмет в инвентаре
                        if GameForm.slots_alias[collected_item[0]] in self.inventory.values[i]:
                            self.inventory.values[i] = self.inventory.values[i][:-1] + str(self.hero.items[collected_item[0]])
                            stacked = True
                            break
                    if not stacked:
                        self.inventory.values.append(GameForm.slots_alias[collected_item[0]] + '  ×' + str(collected_item[1]))

                    self.inventory.footer = f' С Л О Т О В : {len(self.inventory.values)} / 5 '

                keyboard.send('tab')
                self.map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['items'][collected_item[0]] = 0
                self.loc_items.values.pop(index)
                self.loc_items.value = []
                self.items_finder()

                self.inventory.editable = True
                self.action_use.editable = True
                self.action_use.name = ' И С П О Л Ь З О В А Т Ь '
                self.action_use.display()
                self.inventory.display()

                self.inventory_updater()  # Фикс бага с неактивной кнопкой использовать

                if not len(self.loc_items.values):
                    self.loc_items.values = GameForm.slots_loc_default
                    self.loc_items.editable = False
                    self.action_collect.editable = False
                    self.action_collect.when_pressed_function = None
                    self.action_collect.name = 25 * ' '
                    self.loc_items.display()
                    self.action_collect.display()

        else:
            msg = 'Выберите предмет для того, чтобы поднять его.\n|\n|\n|\n|\nДля продолжения нажмите ENTER'
            npyscreen.notify_confirm(msg, title=' НИЧЕГО НЕ ВЫБРАНО ', editw=1, form_color='WARNING')

    def inventory_updater(self):
        """
        Метод, отрисовывающий инвентарь.
        """

        for k, v in self.hero.items.items():
            if not v:
                for i in range(len(self.inventory.values)):
                    if GameForm.slots_alias[k] in self.inventory.values[i]:
                        del self.inventory.values[i]
                        self.inventory.footer = f' С Л О Т О В : {len(self.inventory.values)} / 5 '
                        break
            else:
                for i in range(len(self.inventory.values)):
                    if GameForm.slots_alias[k] in self.inventory.values[i]:
                        self.inventory.values[i] = self.inventory.values[i][:-1] + str(v)

        if not len(self.inventory.values):
            [keyboard.send('shift+tab') for _ in range(6)]
            self.inventory.values = GameForm.slots_inv_default
            self.inventory.value = []
            self.inventory.footer = ' С Л О Т О В : 0 / 5 '
            self.inventory.editable = False
            self.action_use.name = 25 * ' '
            self.action_use.editable = False
            self.action_use.when_pressed_function = None
            self.action_use.display()
        else:
            self.inventory.editable = True  # Фикс бага с головоломкой, после которой инвентарь неактивен
            self.action_use.when_pressed_function = self.use  # Фикс бага с неактивной кнопкой при подборе статуи
            self.action_use.display()

        self.inventory.display()

    def puzzle(self):
        """
        Метод, обрабатывающий головоломку со словами.
        """

        if self.hero.mind < 95 and random.randint(0, 100) > 90:
            self.word_and_ans = word_make()

            self.speaker.value += str("\n    Голоса в голове без остановки повторяют " + self.word_and_ans[1] + '.')
            self.speaker.display()

            self.action_forward.when_pressed_function = None
            self.action_forward.hidden = True
            self.action_forward.display()
            self.action_backward.when_pressed_function = None
            self.action_backward.hidden = True
            self.action_backward.display()
            self.action_right.when_pressed_function = None
            self.action_right.hidden = True
            self.action_right.display()
            self.action_left.when_pressed_function = None
            self.action_left.hidden = True
            self.action_left.display()
            self.action_use.when_pressed_function = None
            self.action_use.hidden = True
            self.action_use.display()
            self.action_collect.when_pressed_function = None
            self.action_collect.hidden = True
            self.action_collect.display()
            self.loc_items.editable = False
            self.loc_items.hidden = True
            self.loc_items.display()
            self.inventory.editable = False
            self.inventory.hidden = True
            self.inventory.display()
            self.quest_bar.hidden = True
            self.quest_bar.display()

            py_win_keyboard_layout.change_foreground_window_keyboard_layout(0x04090409)
            msg = 'Попробуйте восстановить назойливое слово, чтобы восполнить рассудок. \nВведите его в окно, которое вот-вот появится на экране.\nВаша раскладка клавиатуры УЖЕ на АНГЛИЙСКОМ языке.\nДопускается ввод строчных и прописных букв.\nДля ввода дважды нажмте ENTER.\nНажмите ENTER, чтобы продолжить'
            npyscreen.notify_confirm(msg, title=' ГОЛОВОЛОМКА ', editw=1, form_color='STANDOUT')

            self.word_guesser.hidden = False
            self.word_guesser.editable = True
            self.word_guesser.display()
            self.action_enter.name = '  В В Е С Т И  '
            self.action_enter.editable = True
            self.action_enter.display()

            [keyboard.send('shift+tab') for _ in range(5)]

    def enter(self, word_and_ans):
        """
        Метод, обрабатывающий нажатие кнопки ВВЕСТИ.
        """

        self.try_free()

        entered_str = self.word_guesser.value
        if word_guess(self.hero, word_and_ans[0], entered_str):
            msg = 'Вы чувствуете, что не все потеряно!\n|\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить'
            npyscreen.notify_confirm(msg, title=' УСПЕХ ', editw=1, form_color='GOOD')
        else:
            msg = 'Мысли спутываются все сильнее...\n|\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить'
            npyscreen.notify_confirm(msg, title=' НЕУДАЧА ', editw=1, form_color='DANGER')

        self.mind.value = self.hero.mind
        self.mind.display()
        if self.mind.value < 30:
            self.lose()

        self.word_guesser.hidden = True
        self.word_guesser.editable = False
        self.word_guesser.value = ''
        self.word_guesser.display()
        self.action_enter.name = 15 * ' '
        self.action_enter.editable = False
        self.action_enter.display()

        self.action_forward.when_pressed_function = (lambda eventHadled=None: self.move('up'))
        self.action_forward.hidden = False
        self.action_forward.display()
        self.action_backward.when_pressed_function = (lambda eventHandled=None: self.move('down'))
        self.action_backward.hidden = False
        self.action_backward.display()
        self.action_right.when_pressed_function = (lambda eventHandled=None: self.move('right'))
        self.action_right.hidden = False
        self.action_right.display()
        self.action_left.when_pressed_function = (lambda eventHandled=None: self.move('left'))
        self.action_left.hidden = False
        self.action_left.display()
        self.action_use.when_pressed_function = self.use
        self.action_use.hidden = False
        self.action_use.display()
        self.action_collect.when_pressed_function = self.collect
        self.action_collect.hidden = False
        self.action_collect.display()
        self.items_finder()
        self.loc_items.hidden = False
        self.loc_items.display()
        self.inventory.hidden = False
        self.inventory_updater()
        self.quest_bar.hidden = False
        self.quest_bar.display()

        py_win_keyboard_layout.change_foreground_window_keyboard_layout(0x04190419)
        keyboard.send('tab')

    def use(self):
        """
        Метод, обрабатывающий использование разных предметов.
        """

        self.try_free()

        if self.inventory.value:
            index = self.inventory.value[0]
            selected_item = self.inventory.values[index]
            if 'Л Ю М Е Н' in selected_item:
                msg = 'Этот предмет нельзя никак использовать.\nОн обладает пассивной способностью.\n|\n|\n|\nДля продолжения нажмите ENTER'
                npyscreen.notify_confirm(msg, title=' НЕЛЬЗЯ ВОСПОЛЬЗОВАТЬСЯ ', editw=1, form_color='WARNING')
                self.inventory.value = []
                self.inventory.display()
            if 'П Р А Х' in selected_item:
                if result := quests.wall_quest_completion(self.hero, self.quests_dict):
                    self.map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['wall'] = 0
                    self.inventory_updater()
                    self.quest_updater()
                    self.inventory.value = []
                    self.inventory.display()
                    msg = 'Благодаря размазанному праху, стала виднеться надпись: "Статуэтка дарует сон великому злу".\n|\n|\n|\n|\nДля продолжения нажмите ENTER'
                    npyscreen.notify_confirm(msg, title=' ЗАДАНИЕ ВЫПОЛНЕНО ', editw=1, form_color='GOOD')
                else:
                    self.inventory.value = []
                    self.inventory.display()
                    msg = 'Вы не можете использовать это здесь.\nСледуйте сюжетным заданиям.\n|\n|\n|\nДля продолжения нажмите ENTER'
                    npyscreen.notify_confirm(msg, title=' НЕЛЬЗЯ ВОСПОЛЬЗОВАТЬСЯ ', editw=1, form_color='WARNING')
            if 'С Т А Т У Я' in selected_item:
                if result := quests.statue_quest_completion(self.hero, self.quests_dict):
                    self.inventory_updater()
                    self.quest_updater()

                    self.mind.value = self.hero.mind
                    self.mind.display()
                    for i in range(100):
                        self.hero.mind -= 1
                        self.mind.value = self.hero.mind
                        time.sleep(0.01)
                        self.mind.display()

                    self.map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['statue'] = 0
                    self.inventory.value = []
                    self.inventory.display()
                    msg = 'Установленная на место статуя начинает светиться.\nВаш рассудок крепчает.\nТьма, окутывавшая вас отступает.\nИли...\nЧТО ПРОИСХОДИТ!?\nДля продолжения нажмите ENTER'
                    npyscreen.notify_confirm(msg, title=' ЗАДАНИЕ ВЫПОЛНЕНО ', editw=1, form_color='GOOD')
                    [keyboard.send('shift+tab') for _ in range(10)]

                    subprocess.run([sys.executable, f'{SaveSystem.CWD}\outro.py'])

                    SaveSystem.delete_save()
                    self.reset()
                    self.parentApp.registerForm('welcomeMenu', WelcomeForm())
                    self.parentApp.switchForm('welcomeMenu')
                    self.parentApp.removeForm('inGame')
                    [keyboard.send('shift+tab') for _ in range(2)]
                else:
                    msg = 'Вы не можете использовать это здесь.\nСледуйте сюжетным заданиям.\n|\n|\n|\nДля продолжения нажмите ENTER'
                    npyscreen.notify_confirm(msg, title=' НЕЛЬЗЯ ВОСПОЛЬЗОВАТЬСЯ ', editw=1, form_color='WARNING')
                    self.inventory.value = []
                    self.inventory.display()
        else:
            msg = 'Выберите предмет для того, чтобы использовать его.\n|\n|\n|\n|\nДля продолжения нажмите ENTER'
            npyscreen.notify_confirm(msg, title=' НИЧЕГО НЕ ВЫБРАНО ', editw=1, form_color='WARNING')
            self.inventory.value = []
            self.inventory.display()

    def lose(self):
        """
        Метод, обрабатывающий проигрыш.
        """

        msg = 'Глубины забрали Вашу душу...\nНе беспокойтесь о своей жизни. Теперь Вас НЕТ.\nСохранение будет удалено. Весь прогресс утерян.\n|\n|\n|\nНажмите ENTER, чтобы продолжить'
        npyscreen.notify_confirm(msg, title=' ВЫ ПРОИГРАЛИ ', editw=1, form_color='DANGER')

        subprocess.run([sys.executable, f'{SaveSystem.CWD}\lose.py'])

        SaveSystem.delete_save()
        self.reset()
        self.parentApp.registerForm('welcomeMenu', WelcomeForm())
        self.parentApp.switchForm('welcomeMenu')
        self.parentApp.removeForm('inGame')
        [keyboard.send('shift+tab') for _ in range(2)]

    def reset(self):
        """
        Сброс данных при выходе из игровой формы.
        """

        self.hero.quest = "start"
        self.hero.current_quest_coordinates = None
        self.hero.QUEST_CHANGED = False
        self.hero.coordinates = [5, 0]
        self.hero.mind = 100
        self.hero.items = {"light": 0, "figure": 0, "dust": 0}

        self.quests_dict["wall"]["complete"] = False
        self.quests_dict["statue"]["complete"] = False

    def collect_data(self):
        """
        Метод, создающий словарь для сохранения.

        :return -> data: dict
        """

        return {'hero': self.hero,
                'map': self.map_of_world,
                'inventory': (self.inventory.values, self.inventory.footer),
                'finder': self.loc_items.values,
                'quests': self.quests_dict,
                'flags': (self.LUMEN_FLAG, self.DUST_FLAG, self.FIGURE_FLAG, self.MIND_FLAG)}

    def back_to_menu_save(self):
        """
        Выход в меню с сохранением.
        """

        self.try_free()

        if self.frame != 5:  # Проверка прохождения пролога
            msg = 'Сохранение в прологе не доступно.\nЗакончите пролог, прежде, чем сохраняться.\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' ОШИБКА СОХРАНЕНИЯ ', editw=1, form_color='DANGER')
            keyboard.send('ctrl+x')
        else:
            msg = f'Сохранение будет доступно в слоте:\n{SaveSystem.f_name[:-4]}.\nВыйти в меню?'
            if npyscreen.notify_yes_no(msg, title=' ВЫХОД В МЕНЮ ', editw=1, form_color='WARNING'):
                SaveSystem.save_existing(self.collect_data())
                self.reset()
                self.parentApp.registerForm('welcomeMenu', WelcomeForm())
                self.parentApp.switchForm('welcomeMenu')  # Выход в меню
                self.parentApp.removeForm('inGame')  # Удаление покинутой формы из списка зарегистрированных приложением
            else:
                keyboard.send('ctrl+x')

    def back_to_menu(self):
        """
        Выход в стартовое меню без сохранения.
        """

        self.try_free()

        if self.frame == 5:
            msg = 'Вы собираетесь вернуться в меню, не сохранившись.\nВыйти в меню?'
            if npyscreen.notify_yes_no(msg, title=' ВЫХОД В МЕНЮ ', editw=1, form_color='DANGER'):
                SaveSystem.f_name = None
                SaveSystem.loaded_data = None
                SaveSystem.new_save = False
                self.reset()
                self.parentApp.registerForm('welcomeMenu', WelcomeForm())
                self.parentApp.switchForm('welcomeMenu')
                self.parentApp.removeForm('inGame')
            else:
                keyboard.send('ctrl+x')
        else:
            SaveSystem.f_name = None
            SaveSystem.loaded_data = None
            SaveSystem.new_save = False
            self.reset()
            self.parentApp.registerForm('welcomeMenu', WelcomeForm())
            self.parentApp.switchForm('welcomeMenu')
            self.parentApp.removeForm('inGame')

    def exit_save(self):
        """
        Выход с сохранением из меню.
        """

        if self.frame != 5:
            msg = 'Сохранение в прологе не доступно.\nЗакончите пролог, прежде, чем сохраняться.\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' ОШИБКА СОХРАНЕНИЯ ', editw=1, form_color='DANGER')
            keyboard.send('ctrl+x')
        else:
            msg = f'Сохранение будет доступно в слоте:\n{SaveSystem.f_name[:-4]}.\nВыход из ХРАМА совсем не означает Ваше спасение...\nВыйти?'
            if npyscreen.notify_yes_no(msg, title=' ВЫХОД ', editw=1, form_color='WARNING'):
                SaveSystem.save_existing(self.collect_data())
                MapLoaderThread.kill_proccess()
                exit(0)
            else:
                keyboard.send('ctrl+X')

    def exit_no_save(self, eventHandled=None):
        """
        Выход без сохранения из меню.
        """

        self.try_free()

        if self.frame == 4:
            msg = 'Вы собираетесь покинуть игру, не сохранившись.\nВыход из ХРАМА совсем не означает Ваше спасение...\nВыйти?'
            if npyscreen.notify_yes_no(msg, title=' ВЫХОД ', editw=1, form_color='DANGER'):
                MapLoaderThread.kill_proccess()
                exit(0)
            else:
                keyboard.send('ctrl+x')
        else:
            msg = 'Выход из ХРАМА совсем не означает Ваше спасение...\nВыйти?'
            if npyscreen.notify_yes_no(msg, title=' ВЫХОД ', editw=1, form_color='DANGER'):
                MapLoaderThread.kill_proccess()
                exit(0)
            else:
                keyboard.send('ctrl+X')


def main():
    """
    Функция, для запуска игры из cmd по команде temple!
    Прежде являлась точкой входа.
    """

    sys.path.append('path')

    windll.kernel32.SetConsoleTitleW("XPAM")

    window_x = (windll.user32.GetSystemMetrics(0)) // 5
    window_y = (windll.user32.GetSystemMetrics(1)) // 5
    os.system('mode con cols=' + str(window_x) + ' lines=' + str(window_y))
    py_win_keyboard_layout.change_foreground_window_keyboard_layout(0x04190419)  # 0x04090409 - английский язык
    mouse.move(1500, 780)

    subprocess.run([sys.executable, f'{SaveSystem.CWD}\intro.py'])

    MainGameLoop = App()
    MainGameLoop.run()


if __name__ == '__main__':
    main()
