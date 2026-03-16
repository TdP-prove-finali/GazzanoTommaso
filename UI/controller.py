import flet as ft
from UI.view import View
from model.modello import Model
import time
import base64

class Controller:
    def __init__(self, view : View, model : Model):
        self._view = view
        self._model = model

    def fillDDTypes(self):
        lista = self._model.getAllTypes()
        self._view.dd_Types_filter.options = [ft.dropdown.Option(x) for x in lista]
        self._view.update_page()

    # def fillDDProductLines(self):
    #     rtype = self._view.dd_Types_filter.value
    #     lista = self._model.getAllProductLines(rtype)
    #     self._view.dd_ProductLine_filter.options = [ft.dropdown.Option(x) for x in lista]
    #     self._view.update_page()

    def on_filters_changed(self, e):
        rtype = self._view.dd_Types_filter.value

        if not rtype:
            self._view.dd_ProductLine_filter.options = []
            self._view.dd_ProductLine_filter.value = None
            self._view.dd_ProductLine_filter.disabled = True
            self._view.update_page()
            return

        # pls = self._model.getAllProductLines(rtype)
        # self._view.dd_ProductLine_filter.options = [ft.dropdown.Option(pl) for pl in pls]
        # self._view.dd_ProductLine_filter.value = None
        # self._view.dd_ProductLine_filter.disabled = False
        # self._view.update_page()


    def handle_graph(self, e):
        type = self._view.dd_Types_filter.value
        #productLine = self._view.dd_ProductLine_filter.value
        affinity = self._view.sl_affinity_threshold.value
        dateFrom = self._view.dp_from.value
        dateTo = self._view.dp_to.value

        if type is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare una tipologia di rivenditore dal relativo dropdown", color = "red"))
            self._view.update_page()
            return

        # if productLine is None:
        #     self._view.txt_result_temp.controls.clear()
        #     self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare una linea di prodotti dal relativo dropdown", color = "red"))
        #     self._view.update_page()

        if affinity is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare una soglia di affinità dal relativo slider", color = "red"))
            self._view.update_page()
            return

        if dateFrom is None or dateTo is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare una data di partenza / di arrivo", color = "red"))
            self._view.update_page()
            return

        if dateFrom > dateTo:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, la data di partenza non può essere superiore e quella di arrivo", color = "red"))
            self._view.update_page()
            return

        # --- Costruzione Grafo ---
        self._model.buildGraph(type, dateFrom, dateTo, affinity)
        nNodes, nEdges = self._model.getGraphDetails()

        # --- Disegno e Visualizzazione ---
        try:
            img_path = self._model.drawGraphToFile("graph.png")

            with open(img_path, "rb") as f:
                self._view.graph_image.src_base64 = base64.b64encode(f.read()).decode("utf-8")
            self._view.graph_image.visible = True
            self._view.graph_image.update()

            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Grafo correttamente creato, con {nNodes} nodi e {nEdges} archi"))
            self._view.update_page()

        except Exception as e:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Errore nel disegno del grafo: {e}", color = "red"))
            self._view.update_page()



    def on_reset(self, e):
        # azzera selezioni dei filtri
        self._view.dd_Types_filter.value = None
        #self._view.dd_ProductLine_filter.value = None

        # soglia (rimetti default)
        self._view.sl_affinity_threshold.value = 3

        # date (e variabili del controller)
        self._view.dp_from.value = None
        self._view.dp_to.value = None
        self.date_from = None
        self.date_to = None

        # eventuali output/risultati
        if hasattr(self._view, "txt_result_temp"):
            self._view.txt_result_temp.controls.clear()
        if hasattr(self._model, "_graph"):
            self._model._graph.clear()
        if hasattr(self._view, "graph_image"):
            self._view.graph_image.visible = False
            self._view.graph_image.src = ""


        self._view.dd_Types_filter.disabled = False
        #self._view.dd_ProductLine_filter.disabled = False

        self._view.update_page()






