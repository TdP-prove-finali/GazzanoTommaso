import datetime
import flet as ft

class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.sl_max_length = None
        self.dd_Retailer = None
        self.btn_dp_to = None
        self.btn_dp_from = None
        self.dp_to = None
        self.dp_from = None
        self.txt_result_temp = None
        self.btn_reset = None
        self.btn_run_weak = None
        self.btn_run_strong = None
        self.btn_build_graph = None
        self.sl_affinity_threshold = None
        #self.dd_ProductLine_filter = None
        self.dd_Types_filter = None
        self.dd_Country_filter = None
        self.graph_image = None
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

        self.dd_Types_filter = ft.Dropdown(label = "Tipologia di Retailer", hint_text="Seleziona una tipologia", width = 300, on_change=self._controller.on_filters_changed)
        #self.dd_ProductLine_filter = ft.Dropdown(label = "linea di Prodotto", hint_text="Seleziona una linea di prodotto", width = 300, disabled=True)

        self._controller.fillDDTypes()

        self.dp_from = ft.DatePicker(
            first_date=datetime.datetime(2015, 1, 1),
            last_date=datetime.datetime(2018, 12, 31),
            on_change=lambda e: print(f"Giorno selezionato FROM: {e.control.value}")
        )
        self.dp_to = ft.DatePicker(
            first_date=datetime.datetime(2015, 1, 1),
            last_date=datetime.datetime(2018, 12, 31),
            on_change=lambda e: print(f"Giorno selezionato TO: {e.control.value}")
        )

        self._page.overlay.append(self.dp_from)
        self._page.overlay.append(self.dp_to)


        self.btn_dp_from = ft.ElevatedButton(
            "Seleziona data di partenza",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.dp_from.pick_date()
        )
        self.btn_dp_to = ft.ElevatedButton(
            "Seleziona data di arrivo",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.dp_to.pick_date()
        )

        row1 = ft.Row([self.dd_Types_filter], alignment= ft.MainAxisAlignment.CENTER)
        row1_1 = ft.Row([self.btn_dp_from, self.btn_dp_to], alignment= ft.MainAxisAlignment.CENTER)
        self.sl_affinity_threshold = ft.Slider(min = 1, max = 20, divisions=19, value = 3, label = "{value}", width= 300, tooltip="Numero minimo di prodotti in comune per creare un arco")
        row2 = ft.Row([ft.Text("Soglia di Affinità"), self.sl_affinity_threshold], alignment= ft.MainAxisAlignment.CENTER, spacing=20)

        affinity_expl = ft.Container(
            content=ft.Text(
        "Affinità tra retailer: due rivenditori sono collegati se condividono "
                "almeno N prodotti venduti (N = soglia). Il peso dell'arco è il numero "
                "di prodotti in comune. Aumentando la soglia riduci i collegamenti più deboli "
                "e ottieni un grafo più pulito.",
                selectable=False
                    ),padding=10, margin=ft.margin.only(top=5, bottom=5), bgcolor=ft.colors.GREY_200, border_radius=10, width=900)

        self.btn_build_graph = ft.ElevatedButton(text="Crea Grafo", icon=ft.icons.HUB, on_click=self._controller.handle_graph)
        self.btn_run_strong = ft.ElevatedButton(text="Cammino Vincente", icon=ft.icons.TRENDING_UP, disabled=True, on_click=self._controller.handle_camminoVincente)
        self.btn_run_weak = ft.ElevatedButton(text="Cammino Debole", icon=ft.icons.TRENDING_DOWN, disabled=True, on_click=self._controller.handle_camminoDebole)
        self.btn_reset = ft.TextButton(text="Reset Filtri", on_click=self._controller.on_reset)

        self.dd_Retailer = ft.Dropdown(label = "Retailer", hint_text="Seleziona un Retailer", width = 300, on_change=self._controller.on_filters_changed, disabled=True)
        self.sl_max_length = ft.Slider(min=1, max=20, divisions=19, value=3, label="{value}", width=300, tooltip="Numero massimo di archi del cammino ricorsivo", disabled=True)

        row3 = ft.Row([self.btn_build_graph], alignment= ft.MainAxisAlignment.CENTER, spacing=20)
        row3_1 = ft.Row([ self.dd_Retailer,  self.sl_max_length], alignment= ft.MainAxisAlignment.CENTER, spacing=20)
        row3_2 = ft.Row([self.btn_run_strong, self.btn_run_weak, self.btn_reset], alignment= ft.MainAxisAlignment.CENTER, spacing=20)

        self.txt_result_temp = ft.ListView(auto_scroll= False)
        row4 = ft.Row([self.txt_result_temp], alignment= ft.MainAxisAlignment.CENTER, spacing=20)

        self.graph_image = ft.Image(src_base64="", width=1200, fit=ft.ImageFit.CONTAIN, visible=False)
        graph_box = ft.Container(content = self.graph_image,
                                 padding=5, border = ft.border.all(1, ft.colors.BLUE_300), border_radius=10, width=900, height=500)

        row5 = ft.Row([graph_box], alignment= ft.MainAxisAlignment.CENTER)

        #inserisco tutto dentro ad un ft.Column per avere l'interfaccia scrollabile
        main_layout = ft.Column(controls=[row1, row1_1, row2, affinity_expl, row3, row3_1, row3_2, row4, row5], scroll=ft.ScrollMode.AUTO,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing = 15, expand=True)

        self._page.controls.clear()
        self._page.add(main_layout)
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