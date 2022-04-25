# -*- coding: utf-8 -*-

"""
Модуль с интерфейсом для игрового процесса.
"""

import json
import pickle
import npyscreen
import curses
import os
import datetime
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

        self.addForm('MAIN', WelcomeForm, name=' Х Р А М ')
        self.registerForm('welcomeMenu', WelcomeForm())


class SavesPicker(npyscreen.BoxTitle):
    """
    Класс окна выбора сохранения
    """

    _contained_widget = npyscreen.SelectOne


class WelcomeForm(npyscreen.FormBaseNew):
    """
    Класс основной формы.
    """

    helpstr = '    Разработано по мотивам книги "Храм" Говарда Лавкрафта.\n    Ну потом когда-нибудь напишу, мне лень...\n    Два хита по ентеру чтобы вернуться'

    def __init__(self, name=' Х Р А М ', parentApp=App, framed=None,
                 help=helpstr,
                 color='FORMDEFAULT', widget_list=None, cycle_widgets=False,
                 *args, **keywords):
        super().__init__(name, parentApp, framed, help, color, widget_list, cycle_widgets, args, keywords)

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

        saves = os.listdir('saves')
        i = 0
        while i < 5:
            if i < len(saves):
                saves[i] = saves[i][:-4]
            else:
                saves.append('   [ П У С Т О ]')
            i += 1

        self.action_new_game = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 - 3, name='     Н О В А Я  И Г Р А     ', when_pressed_function=self.new_game)
        self.action_load_game = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 - 2, name=' З А Г Р У З И Т Ь  И Г Р У ', when_pressed_function=self.load_btn)
        self.action_exit = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 - 1, name='         В Ы Х О Д          ', when_pressed_function=self.exit)
        self.saves_picker = self.add(SavesPicker, rely=y // 2, relx=(x - 30 - 9 // 2) // 2, max_width=34, max_height=y // 2 - 12, values=saves, editable=False)
        self.action_confirm_selection = self.add(npyscreen.ButtonPress, relx=(x - 28 - 9 // 2) // 2, rely=y // 2 + 8, name='                            ', editable=False)

        self.add(npyscreen.Textfield, value='(build 1.4b)', rely=y - 3, editable=False)

    def new_game(self):
        """
        Начать новую игру.
        """

        if len(os.listdir('saves')) < 5:
            self.parentApp.registerForm('inGame', MainForm())
            self.parentApp.switchForm('inGame')
            self.parentApp.removeForm('welcomeMenu')
        else:
            npyscreen.fmPopup.Popup.SHOW_ATX = (self.useable_space()[1] - 60 - 9 // 2) // 2
            npyscreen.fmPopup.Popup.SHOW_ATY = (self.useable_space()[0] - 12 - 9 // 2) // 2
            msg = 'Допускается создание не более 5-ти сохранений игры.\nДостигнуто максимальное число сохранений\nВойдите в существующую игру или удалите одно из прошлых сохранений.\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' ОШИБКА СОХРАНЕНИЯ ', editw=1, form_color='DANGER')

    def load_btn(self):
        """
        Промежуточная кнопка загрузки игры.
        """
        # TODO чето придумать с остальными кнопками и добавить отмену
        self.action_confirm_selection.editable = True
        self.action_confirm_selection.name = '   В О Й Т И  В  И Г Р У    '
        self.action_confirm_selection.display()
        self.saves_picker.editable = True
        self.saves_picker.display()

    def enter_from_save(self):
        """
        Вход в игру из сохранения
        """
        pass  # TODO написать загрузку

    @staticmethod
    def exit():
        """
        Выход из приложения.
        """

        exit(0)


class Speaker(npyscreen.BoxTitle):
    """
    Основное окно вывода текста.
    """

    _contained_widget = npyscreen.MultiLineEdit

    @staticmethod
    def text_for_storytel(paragraph):
        """
        Возвращает подготовленную к выводу в MultiLineEdit строку.
        """
        # Ширина консольного окна - 137. Символов в спикере - 128. С каждого края - 9/2.

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


class ItemSystem(npyscreen.BoxTitle):
    """
    Обертка для блоков найденных предметов и инвентаря.
    """

    _contained_widget = npyscreen.SelectOne


class MainForm(npyscreen.FormBaseNewWithMenus):
    """
    Класс основной формы.
    """

    frame = 0  # Кадры пролога

    hero = main_hero_class.MainHero()  # Создание персонажа

    npyscreen.wgmultiline.MORE_LABEL = '- еще (↓/↑) -'  # Переопределение надписей
    npyscreen.utilNotify.YesNoPopup.OK_BUTTON_TEXT = 'Да'
    npyscreen.utilNotify.YesNoPopup.CANCEL_BUTTON_TEXT = 'Нет'

    slots_loc_default = ['[ П У С Т О ]']
    slots_inv_default = ['[ П У С Т О ]']  # Дефолтные пустые окна предметов

    slots_alias = {'light': 'Л Ю М Е Н',
                   'figure': 'С Т А Т У Я'}  # Словарь псевдонимов для игровых предметов
    LUMEN_FLAG = 0  # Флаг для подсказки при первом нахождении предмета
    FIGURE_FLAG = 0
    MIND_FLAG = 0  # Подсказка о шкале рассудка

    with open("intro.json", "r") as file:
        full_intro = json.load(file)

    def __init__(self, name=' Х Р А М ', parentApp=App, framed=None,
                 help=WelcomeForm.helpstr,
                 color='FORMDEFAULT', widget_list=None, cycle_widgets=False,
                 *args, **keywords):
        super().__init__(name, parentApp, framed, help, color, widget_list, cycle_widgets, args, keywords)

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
            self._NMDisplay = self.MENU_DISPLAY_TYPE(show_atx=(self.useable_space()[1] - 39 - 9 // 2) // 2, show_aty=(self.useable_space()[0] // 2 - 15) // 2 + 2)
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

        npyscreen.fmPopup.Popup.SHOW_ATX = npyscreen.fmPopup.ActionPopup.SHOW_ATX = (x - 60 - 9 // 2) // 2  # Переопределение координат для всплывающих окон
        npyscreen.fmPopup.Popup.SHOW_ATY = npyscreen.fmPopup.ActionPopup.SHOW_ATY = (y // 2 - 12) // 2 + 1

        storytelling = Speaker.text_for_storytel(self.full_intro[self.frame])

        self.main_menu = self.new_menu(name=' М Е Н Ю ')
        self.main_menu.addItem(text=' СОХРАНИТЬ И ВЫЙТИ В МЕНЮ  ', onSelect=self.back_to_menu_save)
        self.main_menu.addItem(text=' СОХРАНИТЬ И ПОКИНУТЬ ХРАМ ', onSelect=self.exit_save)
        self.main_menu.addItem(text=' ПОКИНУТЬ ХРАМ             ', onSelect=self.exit_no_save)

        self.speaker = self.add(Speaker, editable=False, max_height=y // 2 + 1, rely=1, value=storytelling)

        self.action_forward = self.add(npyscreen.ButtonPress, rely=y // 2 + 2, name='В П Е Р Е Д', when_pressed_function=self.prologue_next_frame)
        self.action_backward = self.add(npyscreen.ButtonPress, rely=y // 2 + 3, name='           ', when_pressed_function=self.prologue_previous_frame, editable=False)
        self.action_right = self.add(npyscreen.ButtonPress, rely=y // 2 + 4, name='           ', when_pressed_function=(lambda: self.move('right')), editable=False)
        self.action_left = self.add(npyscreen.ButtonPress, rely=y // 2 + 5, name='           ', when_pressed_function=(lambda: self.move('left')), editable=False)

        self.quest_bar = self.add(Speaker, value='Еще не было найдено ни \nодного побочного задания.', rely=y // 2 + 2, relx=x // 4, max_width=x // 4 - 2, max_height=y // 2 - 10, editable=False, name=' З А Д А Н И Я ')

        self.loc_items = self.add(ItemSystem, editable=False, name=' Н А Й Д Е Н О ', rely=y // 2 + 2, relx=2 * x // 4, max_width=x // 4 - 2, max_height=y // 2 - 10, values=self.slots_loc_default)

        self.inventory = self.add(ItemSystem, editable=False, name=' И Н В Е Н Т А Р Ь ', rely=y // 2 + 2, relx=3 * x // 4, max_height=y // 2 - 10, max_width=x // 4 - 2, values=self.slots_inv_default, footer=' С Л О Т О В : 0 / 5 ')

        self.action_collect = self.add(npyscreen.ButtonPress, rely=y - 8,  relx=x // 2 + 6,  name='                 ', editable=False, when_pressed_function=self.collect)
        self.action_use = self.add(npyscreen.ButtonPress, rely=y - 8, relx=x - 31, name='                       ', editable=False, when_pressed_function=self.use)

        self.mind = self.add(npyscreen.Slider, editable=False, value=100, lowest=0, step=1, block_color='CAUTIONHL', rely=y - 5)

        self.add(npyscreen.Textfield, value='ШКАЛА РАССУДКА', rely=y - 7, editable=False)
        self.add(npyscreen.Textfield, value='(build 1.4b)', rely=y - 3, editable=False)

    def prologue_next_frame(self):
        """
        Вывод следующего кадра пролога.
        """

        if self.frame < 4:
            self.frame += 1
            if self.frame > 0:
                self.action_backward.editable = True
                self.action_backward.name = 'Н А З А Д  '
                self.action_backward.when_pressed_function = self.prologue_previous_frame
                self.action_backward.display()
            self.speaker.value = Speaker.text_for_storytel(
                self.full_intro[self.frame])
            self.speaker.display()

        elif self.frame == 4:

            msg = 'Вы входите в таинственный ХРАМ.\nЧт@ жд@т вас в#утри?.,.\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' !"##@/..', editw=1, form_color='DANGER')

            msg = 'В одной из комнат Храма Вам предстоит отыскать таинственную статуэтку некоего Божества, чтобы восстановить светлость разума и выбраться из оков глубин...\nДля перемещения по комнатам Храма пользуйтесь предложенными кнопками.\nУправление осуществляется стандартными клавишами (TAB / ENTER / SPACE / ESC) и курсором мыши.\nСкоро вы очнетесь в одной из сотен комнат внутри Храма...\nНажмите ENTER дважды, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' КОНЕЦ ПРОЛОГА ', form_color='WARNING')

            self.speaker.value = Speaker.text_for_storytel(map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1] - 1]['map'])
            self.speaker.display()

            self.action_forward.when_pressed_function = (lambda: self.move('up'))
            self.action_backward.when_pressed_function = (lambda: self.move('down'))
            self.action_right.name = 'В П Р А В О'
            self.action_right.editable = True
            self.action_left.name = 'В Л Е В О  '
            self.action_left.editable = True

            self.action_forward.display()
            self.action_backward.display()
            self.action_right.display()
            self.action_left.display()

    def prologue_previous_frame(self):
        """
        Вывод предыдущего кадра пролога.
        """

        if self.frame > 0:
            self.frame -= 1
            if self.frame == 0:
                self.action_backward.editable = False
                self.action_backward.name = '           '
                self.action_backward.when_pressed_function = None
                self.action_backward.display()
            self.speaker.value = Speaker.text_for_storytel(
                self.full_intro[self.frame])
            self.speaker.display()

    def move(self, key_word):
        """
        Движение вне пролога.
        """

        self.hero.move(key_word)
        self.speaker.value = Speaker.text_for_storytel(description_output(self.hero.coordinates, self.hero.mind))
        self.speaker.display()

        self.items_finder()
        self.inventory_updater()

        self.mind.value = self.hero.mind
        self.mind.display()
        if self.mind.value == 0:  # TODO чето выдумать тут
            msg = 'lose'
            npyscreen.notify_confirm(msg, title='', editw=1, form_color='DANGER')
            exit(0)

        if self.MIND_FLAG == 0 and self.mind.value < 100:
            msg = 'При перемещении по ХРАМУ уровень вашего рассудка будет снижаться на 10 единиц с шансом в 10%\nЧем ниже этот показатель, тем выше шанс, что ваши глаза и уши начнут вас подводить...\nБудьте осторожны!\n|\n|\nДля продолжения нажмите ENTER.'
            npyscreen.notify_confirm(msg, title=' РАССУДОК ', editw=1, form_color='WARNING')
            self.MIND_FLAG += 1

        msg = 'Вы уперлись в СТЕНУ. Не пытайтесь пройти сквозь неё!\nПопытки выбраться за пределы ХРАМА могут плохо сказаться на вашем РАССУДКЕ...\n|\n|\n|\nДля продолжения нажмите ENTER.'
        if key_word == 'up' or key_word == 'down':
            if self.hero.coordinates[1] == 9:
                npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')

            elif self.hero.coordinates[1] == -1:
                npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')
        else:
            if self.hero.coordinates[0] == 0:
                npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')

            elif self.hero.coordinates[0] == 9:
                npyscreen.notify_confirm(msg, title=' ТУПИК ', editw=1, form_color='DANGER')

    def items_finder(self):
        """
        Метод обнаружения предметов на локации.
        """

        self.loc_items.value = []
        self.loc_items.values = self.slots_loc_default
        self.loc_items.editable = False
        self.loc_items.display()
        self.action_collect.editable = False
        self.action_collect.name = '                 '
        self.action_collect.display()
        self.loc_items.display()

        self.slots_loc = []  # Список кортежей ('ПРЕДМЕТ', кол-во) для предметов на каждой локации
        for k, v in map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['items'].items():
            if v >= 1:
                self.slots_loc.append((k, map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['items'][k]))

        if self.slots_loc:
            self.loc_items.values = [(self.slots_alias[self.slots_loc[i][0]] + '  ×' + str(self.slots_loc[i][1])) for i in range(len(self.slots_loc))]
            self.loc_items.editable = True
            self.loc_items.display()

            self.action_collect.editable = True
            self.action_collect.name = 'П О Д О Б Р А Т Ь'
            self.action_collect.when_pressed_function = self.collect
            self.action_collect.display()

            for i in range(len(self.slots_loc)):
                if self.slots_loc[i][0] == 'light' and self.LUMEN_FLAG == 0:
                    msg = 'ЛЮМЕН - ваш лучший друг ... хотя нет, знаете, не самый лучший.\nС шансом в 10% при передвижении по ХРАМУ 1 единица ЛЮМЕНА может загадочным образом исчезнуть из вашего инвентаря, однако, наличие этого источника блеклого света гарантирует стабильность вашего РАССУДКА.\nВ инвентаре может уместиться всего 3 экземпляра.\nДля продолжения нажмите ENTER'
                    self.LUMEN_FLAG = 1
                    npyscreen.notify_confirm(msg, title=' НОВЫЙ ПРЕДМЕТ ', editw=1, form_color='GOOD')
                elif self.slots_loc[i][0] == 'figure' and self.FIGURE_FLAG == 0:
                    msg = 'На своем пути вы нашли манящуюю статуэтку.\nКто знает, может быть она и есть ваше спасение?..\n|\n|\n|\n|\nДля продолжения нажмите ENTER'
                    self.FIGURE_FLAG = 1
                    npyscreen.notify_confirm(msg, title=' НОВЫЙ ПРЕДМЕТ ', editw=1, form_color='GOOD')

    def collect(self):
        """
        Метод, обрабатывающий сбор предметов по кнопке ПОДОБРАТЬ.
        """

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
                if self.inventory.values == self.slots_inv_default:  # Если инвентарь пустой
                    self.inventory.values = [self.slots_alias[collected_item[0]] + '  ×' + str(collected_item[1])]
                    self.inventory.footer = f' С Л О Т О В : {len(self.inventory.values)} / 5 '
                    self.inventory.display()
                else:
                    stacked = False
                    for i in range(len(self.inventory.values)):  # Проверка, есть ли уже такой предмет в инвентаре
                        if self.slots_alias[collected_item[0]] in self.inventory.values[i]:
                            self.inventory.values[i] = self.inventory.values[i][:-1] + str(self.hero.items[collected_item[0]])
                            stacked = True
                            break
                    if not stacked:
                        self.inventory.values.append(self.slots_alias[collected_item[0]] + '  ×' + str(collected_item[1]))

                    self.inventory.footer = f' С Л О Т О В : {len(self.inventory.values)} / 5 '
                    self.inventory.display()

                map_of_world[self.hero.coordinates[0]][self.hero.coordinates[1]]['items'][collected_item[0]] = 0
                del self.loc_items.values[index]
                self.loc_items.value = []

                self.inventory.editable = True
                self.action_use.editable = True
                self.action_use.name = 'И С П О Л Ь З О В А Т Ь'
                self.action_use.display()
                self.inventory.display()

                if len(self.loc_items.values) == 0:
                    self.loc_items.values = self.slots_loc_default
                    self.loc_items.editable = False
                    self.action_collect.editable = False
                    self.action_collect.when_pressed_function = None
                    self.action_collect.name = '                 '
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
            if v == 0:
                for i in range(len(self.inventory.values)):
                    if self.slots_alias[k] in self.inventory.values[i]:
                        del self.inventory.values[i]
                        self.inventory.footer = f' С Л О Т О В : {len(self.inventory.values)} / 5 '
                        break
            else:
                for i in range(len(self.inventory.values)):
                    if self.slots_alias[k] in self.inventory.values[i]:
                        self.inventory.values[i] = self.inventory.values[i][:-1] + str(v)

        if len(self.inventory.values) == 0:
            self.inventory.values = self.slots_inv_default
            self.inventory.value = []
            self.inventory.footer = ' С Л О Т О В : 0 / 5 '
            self.inventory.editable = False
            self.action_use.name = '                       '
            self.action_use.editable = False
            self.action_use.when_pressed_function = None
            self.action_use.display()

        self.inventory.display()

    def use(self):
        """
        Метод, обрабатывающий использование разных предметов
        """
        pass  # TODO ну тут все ясно

    def back_to_menu_save(self):
        """
        Выход в меню с сохранением.
        """

        if len(os.listdir('saves')) < 5:  # Ограничение на создание не более 5-ти сохранений
            f_name = 'SAVE ' + str(datetime.datetime.now())[:-7].replace(':', '-', 3)
            with open(fr'saves\{f_name}.dat', 'wb') as f:
                pickle.dump([self.hero, ], f)  # Сохранение объекта класса формы

            self.parentApp.registerForm('welcomeMenu', WelcomeForm())
            self.parentApp.switchForm('welcomeMenu')  # Выход в меню
            self.parentApp.removeForm('inGame')  # Удаление покинутой формы из списка зарегистрированных приложением
        else:
            msg = 'Допускается создание не более 5-ти сохранений игры.\nДостигнуто максимальное число сохранений\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' ОШИБКА СОХРАНЕНИЯ ', editw=1, form_color='DANGER')

    def exit_save(self):
        """
        Выход с сохранением из меню.
        """

        if len(os.listdir('saves')) < 5:
            f_name = 'SAVE ' + str(datetime.datetime.now())[:-7].replace(':', '-', 3)
            with open(fr'saves\{f_name}.dat', 'wb') as f:
                pickle.dump([self.hero, ], f)
            exit(0)
        else:
            msg = 'Допускается создание не более 5-ти сохранений игры.\nДостигнуто максимальное число сохранений\n|\n|\n|\n|\nНажмите ENTER, чтобы продолжить.'
            npyscreen.notify_confirm(msg, title=' ОШИБКА СОХРАНЕНИЯ ', editw=1,
                                     form_color='DANGER')

    @staticmethod
    def exit_no_save():
        """
        Выход без сохранения из меню.
        """

        msg = 'Вы собираетесь покинуть игру, не сохранившись.\nВы уверены?'
        if npyscreen.notify_yes_no(msg, title=' ВЫХОД ', editw=1, form_color='DANGER'):
            exit(0)


if __name__ == '__main__':
    windll.kernel32.SetConsoleTitleW(" X P A M ")

    window_x = (windll.user32.GetSystemMetrics(0)) // 5
    window_y = (windll.user32.GetSystemMetrics(1)) // 5
    os.system('mode con cols=' + str(window_x) + ' lines=' + str(window_y))  # Принтануть размеры которые он использует и зафиксировать их, чтобы не скейлить)

    MyApp = App()
    MyApp.run()
