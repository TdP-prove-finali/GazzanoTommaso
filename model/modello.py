import copy

import networkx as nx
from pyparsing import nestedExpr

from database.DAO import DAO
import matplotlib.pyplot as plt
import os

class Model:
    def __init__(self):
        self._retailer = []
        self._idMap = {}
        self._graph = nx.Graph()

    def getAllRetailer(self, rtype, dateFrom, dateTo):
        '''
        Salvataggio in lista e mappa dei Retailer che soddisfano i requisiti scelti dall'utente
        :param rtype: str
        :param productLine: str
        :param dateFrom: datetime.datetime
        :param dateTo: datetime.datetime
        :return: Retailer
        '''
        self._retailer =  DAO.getAllRetailers(rtype, dateFrom, dateTo)
        for retailer in self._retailer:
            self._idMap[retailer.Retailer_code] = retailer

    def getAllEdges(self, rtype, dateFrom, DateTo, Affinity):
        '''
        Metodo che ritorna tutti gli archi tra i nodi scelti estrandoli dal DAO
        :param rtype: str
        :param dateFrom: datetime.datetime
        :param DateTo: datetime.datetime
        :param Affinity: integer
        :return: list(tuple)
        '''
        return DAO.getAllEdges(rtype, dateFrom, DateTo, Affinity)


    def getAllTypes(self):
        '''
        Metodo che ritorna tutte le singole tipologie di Retailer presenti estratti nel DAO
        :return: list(str)
        '''
        return DAO.getAllTypes()
    # def getAllProductLines(self,rtype):
    #     '''
    #     Metodo che ritorna le singole ProductLines specifiche alla tipologia di retailer selezionata dall'utente
    #     :param rtype: str
    #     :return: list(str)
    #     '''
    #     return DAO.getAllProductLines(rtype)

    def addAllEdges(self, rtype, dateFrom, dateTo, affinity):
        edges = self.getAllEdges(rtype, dateFrom, dateTo, affinity)
        for r1, r2, w in edges:
            if r1 in self._idMap and r2 in self._idMap:
                n1 = self._idMap[r1]
                n2 = self._idMap[r2]

                self._graph.add_edge(n1, n2, weight=w)


    def buildGraph(self, rtype, dateFrom, dateTo, affinity):
        self._graph.clear()
        self.getAllRetailer(rtype, dateFrom, dateTo)
        self._graph.add_nodes_from(self._retailer)
        self.addAllEdges(rtype, dateFrom, dateTo, affinity)

    def drawGraphToFile(self, outpath: str = "graph.png") -> str:
        '''
        Disegna il grafo creato salvandolo in un file png
        :param outpath: percorso del file PNG di output
        :return: percorso del file PNG
        '''

        if self._graph.number_of_nodes() == 0:
            raise ValueError("Grafo vuoto, niente da disegnare")

        isolated_nodes  = list(nx.isolates(self._graph))
        self._graph.remove_nodes_from(isolated_nodes)

        if self._graph.number_of_nodes() == 0:
            raise ValueError("Nessun nodo connesso da disegnare")


        pos = nx.circular_layout(self._graph)
        fig, ax = plt.subplots(figsize=(14.4, 10))
        nx.draw(self._graph, pos=pos, ax=ax,  with_labels=False, node_size=300, arrows=False)

        labels ={n: str(n) for n in self._graph.nodes()}
        labels_pos = {n: (pos[n][0] * 1.08, pos[n][1]*1.08) for n in self._graph.nodes()}

        nx.draw_networkx_labels(self._graph, pos=labels_pos, labels=labels, font_size=12, ax=ax)

        edges_labels = nx.get_edge_attributes(self._graph, 'weight')
        nx.draw_networkx_edge_labels(self._graph, pos=pos, ax=ax,  edge_labels=edges_labels, font_size=10)

        ax.set_axis_off() #disattiva gli assi cartesiani che in matplot ci sono di default
        plt.margins(0.20) #margine del png che viene aggiunto durante la scrittura del file
        plt.savefig(outpath, dpi=200, bbox_inches='tight') # il tight va a togliere parte del bordo bianco creato dal margin -> lo lascio comunque
        # perché taglia anche parte delle etichette dei nodi che sono fondamentali
        plt.close()

        return os.path.abspath(outpath)

    def getGraphDetails(self):
        return self._graph.number_of_nodes(), self._graph.number_of_edges()


    def getCamminoVincente(self, retailer_partenza, maxLength):
        '''
        Algoritmo che va a identificare le sequenze forti che vanno a massimizzare i pesi degli archi (affinità) tra i nodi (retailer)
        :param retailer_partenza: Nodo di Partenza scelto dall'utente
        :param maxLength: lunghezza massima del cammino
        :return: tupla comprensiva di lista contenente tutti i nodi e valore del peso della sequenza
        '''
        self._bestPath = []
        self._bestWeight = 0

        parziale = [retailer_partenza]
        self.ricorsioneCamminoVincente(retailer_partenza, parziale, 0, maxLength)
        return self._bestPath, self._bestWeight

    def getCamminoDebole(self, retailer_partenza, maxLength):
        '''
        Algoritmo che va a indentificare le sequenze deboli che vanno a minimizzare i pesi degli archi (affinità) tra i nodi (retailer)
        :param retailer_partenza: Nodo di Partenza scelto dall'utente
        :param maxLength: lunghezza massima del cammino
        :return: tupla comprensiva di lista contenente tutti i nodi e valore del peso della sequenza
        '''
        self._worstPath = []
        self._worstWeight = float('inf')  #inizializzo per minimizzare

        parziale = [retailer_partenza]
        self.ricorsioneCamminoDebole(retailer_partenza, parziale, 0, maxLength)
        return self._worstPath, self._worstWeight


    def ricorsioneCamminoVincente(self, nodoCorrente, parziale, pesoCorrente, maxLength):

        if pesoCorrente > self._bestWeight:
            self._bestWeight = pesoCorrente
            self._bestPath = copy.deepcopy(parziale)

        if len(parziale)-1  == maxLength:
            return

        for n in self._graph.neighbors(nodoCorrente):
            if n not in parziale:
                pesoArco = self._graph[nodoCorrente][n]["weight"]
                parziale.append(n)
                self.ricorsioneCamminoVincente(n, parziale, pesoCorrente + pesoArco, maxLength)
                parziale.pop()

    def ricorsioneCamminoDebole(self, nodoCorrente, parziale, pesoCorrente, maxLength):
        if len(parziale)-1 == maxLength:
            if pesoCorrente < self._worstWeight:
                self._worstWeight = pesoCorrente
                self._worstPath = copy.deepcopy(parziale)
            return

        for n in self._graph.neighbors(nodoCorrente):
            if n not in parziale:
                pesoArco = self._graph[nodoCorrente][n]["weight"]
                parziale.append(n)
                self.ricorsioneCamminoDebole(n, parziale, pesoCorrente + pesoArco, maxLength)
                parziale.pop()

    def drawBestPathToFile(self, bestPath, outpath: str = "best_path.png") -> str:
        '''
        Disegna il grafo complessivo, evidenziando il cammino vincente trovato con la ricorsione
        :param BestPath: lista dei nodi del cammino vincente
        :param outpath: nome file png di output
        :return: percorso assoluto del file
        '''
        if self._graph.number_of_nodes() == 0:
            raise ValueError("Grafo vuoto, niente da disegnare")

        isolated_nodes = list(nx.isolates(self._graph))
        self._graph.remove_nodes_from(isolated_nodes)

        if self._graph.number_of_nodes() == 0:
            raise ValueError("Nessun nodo connesso da disegnare")

        if bestPath is None or len(bestPath) == 0:
            raise ValueError("Cammino Vuoto, niente da Evidenziare")

        pos = nx.circular_layout(self._graph)
        fig, ax = plt.subplots(figsize=(14.4, 10))

        #nodi normali
        nx.draw_networkx_nodes(self._graph, pos, ax = ax, node_size=300)
        #archi normali
        nx.draw_networkx_edges(self._graph, pos, ax = ax, edge_color='lightgray', width=1.5)

        #archi del cammino
        path_edges = []
        for i in range(len(bestPath)-1):
            u = bestPath[i]
            v = bestPath[i + 1]
            if self._graph.has_edge(u, v):
                path_edges.append((u, v))
        nx.draw_networkx_edges(self._graph, pos, path_edges, edge_color='Green', width=3)

        #nodi del cammino evidenziali
        nx.draw_networkx_nodes(self._graph, pos, ax = ax, nodelist = bestPath, node_size=300)

        labels = {n: n.Retailer_name for n in self._graph.nodes()}
        nx.draw_networkx_labels(self._graph, pos = pos,ax=ax,  labels=labels, font_size=12)

        edges_labels = nx.get_edge_attributes(self._graph, 'weight')
        nx.draw_networkx_edge_labels(self._graph, pos=pos, ax=ax, edge_labels=edges_labels, font_size=10)


        ax.set_axis_off()
        plt.margins(0.20)
        plt.savefig(outpath, dpi=200, bbox_inches='tight')
        plt.close()
        return os.path.abspath(outpath)

    def drawWorstPathToFile(self, worstPath, outpath: str = "worst_path.png") -> str:
        '''
        Disegna il grafo complessivo, evidenziando il cammino debole trovato con la ricorsione
        :param worstPath: lista dei nodi del cammino debole
        :param outpath: nome file png di output
        :return: percorso assoluto del file
        '''
        if self._graph.number_of_nodes() == 0:
            raise ValueError("Grafo vuoto, niente da disegnare")

        isolated_nodes = list(nx.isolates(self._graph))
        self._graph.remove_nodes_from(isolated_nodes)

        if self._graph.number_of_nodes() == 0:
            raise ValueError("Nessun nodo connesso da disegnare")

        if worstPath is None or len(worstPath) == 0:
            raise ValueError("Cammino Vuoto, niente da Evidenziare")

        pos = nx.circular_layout(self._graph)
        fig, ax = plt.subplots(figsize=(14.4, 10))

        #nodi normali
        nx.draw_networkx_nodes(self._graph, pos, ax = ax, node_size=300)
        #archi normali
        nx.draw_networkx_edges(self._graph, pos, ax = ax, edge_color='lightgray', width=1.5)

        #archi del cammino
        path_edges = []
        for i in range(len(worstPath)-1):
            u = worstPath[i]
            v = worstPath[i + 1]
            if self._graph.has_edge(u, v):
                path_edges.append((u, v))
        nx.draw_networkx_edges(self._graph, pos, path_edges, edge_color='Red', width=3)

        #nodi del cammino evidenziali
        nx.draw_networkx_nodes(self._graph, pos, ax = ax, nodelist = worstPath, node_size=300)

        labels = {n: n.Retailer_name for n in self._graph.nodes()}
        nx.draw_networkx_labels(self._graph, pos = pos,ax=ax,  labels=labels, font_size=12)

        edges_labels = nx.get_edge_attributes(self._graph, 'weight')
        nx.draw_networkx_edge_labels(self._graph, pos=pos, ax=ax, edge_labels=edges_labels, font_size=10)


        ax.set_axis_off()
        plt.margins(0.20)
        plt.savefig(outpath, dpi=200, bbox_inches='tight')
        plt.close()
        return os.path.abspath(outpath)








