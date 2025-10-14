import flet as ft

class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()

        #page stuff
        self._page = page
        self._page.title = "Tommaso Gazzano s313657 - Prova Finale"
        self._page.horizontal_alignment = 'CENTER'
        self._page.window_width = 1200
        self._page.window_height = 900
        self._page.window_center()
        self._page.theme_mode = ft.ThemeMode.LIGHT
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None

    def load_interface(self):

        #interface stuff
        self._page.update()


    def controller(self):
        return self._controller

    def set_controller(self, controller):
        self._controller  = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title = ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()