import networkx as nx
from database.DAO import DAO

class Model:
    def __init__(self):
        self._retailer = []
        self._idMap = {}
        self._graph = nx.DiGraph()

    def getAllRetailer(self, rtype, productLine, dateFrom, dateTo):
        '''
        Salvataggio in lista e mappa dei Retailer che soddisfano i requisiti scelti dall'utente
        :param rtype: str
        :param productLine: str
        :param dateFrom: datetime.datetime
        :param dateTo: datetime.datetime
        :return: Retailer
        '''
        self._retailer =  DAO.getAllRetailers(rtype, productLine, dateFrom, dateTo)
        for retailer in self._retailer:
            self._idMap[retailer.Retailer_code] = retailer


    def getAllTypes(self):
        '''
        Metodo che ritorna tutte le singole tipologie di Retailer presenti estratti nel DAO
        :return: list(str)
        '''
        return DAO.getAllTypes()
    def getAllProductLines(self,rtype):
        '''
        Metodo che ritorna le singole ProductLines specifiche alla tipologia di retailer selezionata dall'utente
        :param rtype: str
        :return: list(str)
        '''
        return DAO.getAllProductLines(rtype)

    def buildGraph(self, rtype, productLine, dateFrom, dateTo, affinity):
        self._graph.clear()
        self.getAllRetailer(rtype, productLine, dateFrom, dateTo)
        self._graph.add_nodes_from(self._retailer)

    def getGraphDetails(self):
        return self._graph.number_of_nodes(), self._graph.number_of_edges()




