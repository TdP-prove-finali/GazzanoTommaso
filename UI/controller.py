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

    def fillDDRetailer(self):
        lista = [n for n in self._model._graph.nodes() if self._model._graph.degree(n) > 0]
        self._view.dd_Retailer.options = [
            ft.dropdown.Option(key=str(x.Retailer_code), text=x.Retailer_name)
            for x in lista
        ]
        self._view.update_page()


    def handle_graph(self, e):
        type = self._view.dd_Types_filter.value
        affinity = self._view.sl_affinity_threshold.value
        dateFrom = self._view.dp_from.value
        dateTo = self._view.dp_to.value

        # --- validazione dei parametri inseriti dall'utente ---
        if type is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare una tipologia di rivenditore dal relativo dropdown", color = "red"))
            self._view.update_page()
            return


        if dateFrom is None or dateTo is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare una data di partenza / di arrivo", color = "red"))
            self._view.update_page()
            return

        if dateFrom > dateTo:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, la data di partenza non può essere successiva e quella di arrivo", color = "red"))
            self._view.update_page()
            return

        # --- Costruzione Grafo ---
        self._model.buildGraph(type, dateFrom, dateTo, affinity)
        nNodes, nEdges = self._model.getGraphDetails()
        self.fillDDRetailer()
        self._view.dd_Retailer.disabled = False
        self._view.sl_max_length.disabled = False
        self._view.btn_run_strong.disabled = False
        self._view.btn_run_weak.disabled = False
        self._view.sl_max_length.disabled = False

        # --- Disegno e Visualizzazione ---
        try:
            img_path = self._model.drawGraphToFile("graph.png")
            # conversione dell'immagine PNG in base64 per visualizzarla in Flet
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
        # --- ripristina i filtri a valori iniziali ---
        self._view.dd_Types_filter.value = None
        self._view.sl_affinity_threshold.value = 3

        self._view.dp_from.value = None
        self._view.dp_to.value = None
        self.date_from = None
        self.date_to = None
        self._view.dd_Retailer.value = None

        # ripristino di eventuali output/risultati
        if hasattr(self._view, "txt_result_temp"):
            self._view.txt_result_temp.controls.clear()
        if hasattr(self._model, "_graph"):
            self._model._graph.clear()
        if hasattr(self._view, "graph_image"):
            self._view.graph_image.visible = False
            self._view.graph_image.src = ""

        self._view.dd_Types_filter.disabled = False
        self._view.update_page()


    def handle_camminoVincente(self, e):
        retailer_id = self._view.dd_Retailer.value
        maxLength = self._view.sl_max_length.value

        if retailer_id is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare un retailer di partenza", color = "red"))
            self._view.update_page()
            return

        if maxLength is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare una lunghezza massima del cammino", color="red"))
            self._view.update_page()
            return

        nodo_partenza = self._model._idMap[int(retailer_id)]
        bestPath, bestWeight = self._model.getCamminoVincente(nodo_partenza, int(maxLength))

        if not bestPath:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Nessuno cammino trovato", color="red"))
            self._view.update_page()
            return

        try:
            img_path = self._model.drawBestPathToFile(bestPath, "best_path.png")
            with open(img_path, "rb") as f:
                self._view.graph_image.src_base64 = base64.b64encode(f.read()).decode("utf-8")
            self._view.graph_image.visible = True
            self._view.graph_image.update()

            topThree = self._model.getTopProductsPath(bestPath, self._view.dp_from.value, self._view.dp_to.value)
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Peso trovato: {bestWeight}"))
            self._view.txt_result_temp.controls.append(ft.Text("Top 3 Prodotti del cammino vincente:"))
            for codice, nome, occ in topThree:
                self._view.txt_result_temp.controls.append(ft.Text(f" - {codice} - {nome} ({occ} occorrenze)"))
            self._view.update_page()

        except Exception as e:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(
                ft.Text(f"Errore nel disegno del cammino: {e}", color="red"))
            self._view.update_page()

    def handle_camminoDebole(self, e):
        retailer_id = self._view.dd_Retailer.value
        maxLength = self._view.sl_max_length.value

        if retailer_id is None:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Attenzione, selezionare un retailer di partenza", color = "red"))
            self._view.update_page()
            return


        #recupera il nodo di partenza dalla mappa tramite il codice retailer selezionato
        nodo_partenza = self._model._idMap[int(retailer_id)]
        worstPath,worstWeight = self._model.getCamminoDebole(nodo_partenza, int(maxLength))

        if not worstPath:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Nessuno cammino trovato", color="red"))
            self._view.update_page()
            return

        try:
            img_path = self._model.drawWorstPathToFile(worstPath, "worst_path.png")
            with open(img_path, "rb") as f:
                self._view.graph_image.src_base64 = base64.b64encode(f.read()).decode("utf-8")
            self._view.graph_image.visible = True
            self._view.graph_image.update()

            bottomThree = self._model.getBottomProductsPath(worstPath, self._view.dp_from.value, self._view.dp_to.value)

            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(ft.Text(f"Peso trovato: {worstWeight}"))
            self._view.txt_result_temp.controls.append(ft.Text("Bottom 3 Prodotti del cammino debole:"))
            for codice, nome, occ in bottomThree:
                self._view.txt_result_temp.controls.append(ft.Text(f" - {codice} - {nome} ({occ} occorrenze)"))
            self._view.update_page()

        except Exception as e:
            self._view.txt_result_temp.controls.clear()
            self._view.txt_result_temp.controls.append(
                ft.Text(f"Errore nel disegno del cammino: {e}", color="red"))
            self._view.update_page()










