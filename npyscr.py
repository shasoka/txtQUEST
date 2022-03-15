#
# import npyscreen
#
#
# class App(npyscreen.StandardApp):
#     def onStart(self):
#         self.addForm("MAIN", MainForm, name="ХРАМ")
#
#
# class MainForm(npyscreen.ActionForm):
#     npyscreen.ActionForm.OK_BUTTON_TEXT = 'ВЫХОД'
#     npyscreen.ActionForm.CANCEL_BUTTON_TEXT = 'бесполезая кнопка'
#
#     def create(self):
#         self.title = self.add(npyscreen.TitleText, name="оно работает", value="спасибо")
#         self.add(npyscreen.TitleSelectOne, rely=40, max_height=3, value = [1,], name="Pick One",
#                 values = ["Продолжить","Новая игра","Выйти"], scroll_exit=True)
#
#
#     def on_ok(self):
#         self.parentApp.setNextForm(None)
#
#     def on_cancel(self):
#         self.title.value = "=)"
#
#
# if __name__ == '__main__':
#     MyApp = App()
#     MyApp.run()


import npyscreen
import curses


class App(npyscreen.StandardApp):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="ХРАМ")


class InputBox1(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit
    # def when_value_edited(self):
    #     self.parent.parentApp.queue_event(npyscreen.Event("event_value_edited"))


class InputBox2(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit


class MainForm(npyscreen.ActionForm):
    npyscreen.ActionForm.OK_BUTTON_TEXT = 'ВЫЙТИ'
    npyscreen.ActionForm.CANCEL_BUTTON_TEXT = 'ы'



    def create(self):
        self.add_event_hander("event_value_edited", self.event_value_edited)
        new_handlers = {
            # Устанавливаем ctrl+Q для выхода
            "^Q": self.exit_func,
            # Устанавливаем alt+enter для очистки inputbox
            # curses.ascii.alt(curses.ascii.NL): self.inputbox_clear
        }
        self.add_handlers(new_handlers)

        y, x = self.useable_space()
        # self.InputBox1 = self.add(InputBox1, max_height=y // 2, )
        self.InputBox2 = self.add(InputBox2, editable=False, max_height=y // 2)
        self.add(npyscreen.TitleSelectOne, rely=27, max_height=3, max_value=[1, ],
                 name="Ваш выбор", values = ["Продолжить","Новая игра","Выйти"], scroll_exit=True)

    def event_value_edited(self, event):
        self.InputBox2.value = self.InputBox1.value
        self.InputBox2.display()

    def on_ok(self):
        self.parentApp.setNextForm(None)

    def on_cancel(self):
        self.title.value = "=)"

    def inputbox_clear(self, _input):
        self.InputBox1.value = self.InputBox2.value = ""
        self.InputBox1.display()
        self.InputBox2.display()

    def exit_func(self, _input):
        exit(0)


MyApp = App()
MyApp.run()
