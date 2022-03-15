
import npyscreen


class App(npyscreen.StandardApp):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="ПОБЕДА")


class MainForm(npyscreen.ActionForm):
    def create(self):
        self.title = self.add(npyscreen.TitleText, name="наконец-то", value="спасибо")

    def on_ok(self):
        self.parentApp.setNextForm(None)

    def on_cancel(self):
        self.title.value = "=)"


MyApp = App()
MyApp.run()
