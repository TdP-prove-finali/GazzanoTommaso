import networkx as nx
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
        Disegna il grafo creato salvandolo in un file pgn
        :param outpath: percorso del file PNG di output
        :return: percorso del file PNG
        '''

        if self._graph.number_of_nodes() == 0:
            raise ValueError("Grafo vuoto, niente da disegnare")


        pos = nx.circular_layout(self._graph)
        fig, ax = plt.subplots(figsize=(14.4, 8)) # ho usato questi pollici perché hanno la stessa proporzione delle domensioni del container in cui si trova l'img!
        nx.draw(self._graph, pos=pos, ax=ax,  with_labels=False, node_size=300, arrows=False)

        labels ={n: str(n) for n in self._graph.nodes()}
        labels_pos = {n: (pos[n][0] * 1.15, pos[n][1]*1.15) for n in self._graph.nodes()}

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




