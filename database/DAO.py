from idlelib.debugger_r import IdbAdapter

from database.DB_connect import DBConnect
from model.Retailer import Retailer


class DAO():
    @staticmethod
    def getAllRetailers(type, dateFrom, dateTo):
        '''
        metodo che estrae dal Database tutti i retailer che soddisfano i requisiti scelti dall'utente attraverso i filtri
        dell'interfaccia grafica
        :param type: str
        :param productLine: str
        :param dateFrom: datetime.datetime
        :param dateTo: datetime.datetime
        :return: list(Retailer)
        '''
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione Fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = '''SELECT DISTINCT
                            r.Retailer_code,
                            r.Retailer_name,
                            r.Type,
                            r.Country
                        FROM
                            go_retailers r,
                            go_daily_sales ds,
                            go_products p
                        WHERE
                            r.Retailer_code = ds.Retailer_code
                            AND ds.Product_number = p.Product_number
                            AND r.Type = %s
                            AND ds.Date BETWEEN %s AND %s
                        ORDER BY
                            r.Retailer_code'''
            cursor.execute(query, (type, dateFrom, dateTo))

            for row in cursor:
                result.append(Retailer(row["Retailer_code"], row["Retailer_name"], row["Type"], row["Country"]))

            cursor.close()
            cnx.close()
        return result



    @staticmethod
    def getAllTypes():
        '''
        Estrazione dal Database delle tipologie di Retailer presenti
        :return: list(str)
        '''
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione Fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = "select DISTINCT gr.`Type` as t from go_retailers gr "

            cursor.execute(query)

            for row in cursor:
                result.append(row["t"])

            cursor.close()
            cnx.close()
        return result


    @staticmethod
    def getAllEdges(rtype, dateFrom, dateTo, Affinity):
        '''
        Estrazione dal DB di tutti gli archi del grafo
        :param rtype: tipologia Retailer
        :param dateFrom: data di partenza della ricerca
        :param dateTo: data di fine delal ricerca
        :param Affinity: numero minimo di prodotti che due retailer devono avere in comune
        :return: liste di tuple nella forma (nodo1, nodo2, peso arco)
        '''

        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione Fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT
                            a.Retailer_code AS r1,
                            b.Retailer_code AS r2,
                            COUNT(DISTINCT a.Product_number) AS affinity
                        FROM
                            (
                                SELECT DISTINCT r.Retailer_code, ds.Product_number
                                FROM
                                    go_retailers r,
                                    go_daily_sales ds,
                                    go_products p
                                WHERE
                                    r.Retailer_code = ds.Retailer_code
                                    AND ds.Product_number = p.Product_number
                                    AND r.`Type` = %s
                                    AND ds.`Date` BETWEEN %s AND %s) a,
                            (   SELECT DISTINCT r.Retailer_code, ds.Product_number
                                FROM
                                    go_retailers r,
                                    go_daily_sales ds,
                                    go_products p
                                WHERE
                                    r.Retailer_code = ds.Retailer_code
                                    AND ds.Product_number = p.Product_number
                                    AND r.`Type` = %s
                                    AND ds.`Date` BETWEEN %s AND %s) b
                        WHERE
                            a.Product_number = b.Product_number
                            AND a.Retailer_code < b.Retailer_code
                        GROUP BY
                            a.Retailer_code, b.Retailer_code
                        HAVING
                            COUNT(DISTINCT a.Product_number) >= %s
                        ORDER BY
                            affinity DESC, r1, r2"""
            cursor.execute(query, (rtype, dateFrom, dateTo, rtype, dateFrom, dateTo, Affinity))
            for row in cursor:
                result.append((row["r1"], row["r2"], row["affinity"]))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def getTopProductsPath(path, dateFrom, dateTo):
        '''
        Estrazione dei tre prodotti che compaiono maggiormente nel cammino vincente
        :param path: cammino vincente trovato secondo i parametri della ricerca
        :param dateFrom: data di partenza della ricerca
        :param dateTo: data di fine della ricerca
        :return: lista di tuple nella forma (codice prodotto, nome prodotto, numero di occorrenze)
        '''
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione Fallita")
        else:
            cursor = cnx.cursor(dictionary=True)

            conditions = []
            params = []

            # queste due liste e la join che si trova sotto permettono di rendere modulare la ricerca dei prodotti
            # vincenti, dal momento che a priori non sappiamo la lunghezza del cammino scelto dall'utente tramite lo slider

            for i in range(len(path)-1):
                conditions.append("ds1.Retailer_code = %s AND ds2.Retailer_code = %s")
                params.append(path[i].Retailer_code)
                params.append(path[i+1].Retailer_code)

            where_pairs = " OR ".join(conditions)
            # OR.join() permette di andare a prendere tutti i prodotti condivisi tra qualsiasi coppia consecutiva del path

            query = f"""SELECT
                            p.Product_number,
                            p.Product,
                            COUNT(*) AS occorrenze
                        FROM 
                            go_daily_sales ds1,
                            go_daily_sales ds2,
                            go_products p
                        WHERE 
                            ds1.Product_number = ds2.Product_number
                            AND ds1.Product_number = p.Product_number
                            AND ({where_pairs})
                            AND ds1.Date BETWEEN %s AND %s
                            AND ds2.Date BETWEEN %s AND %s
                
                        GROUP BY 
                            p.Product_number,
                            p.Product
                        ORDER BY 
                            occorrenze DESC
                            LIMIT 3"""

            params.append(dateFrom)
            params.append(dateTo)
            params.append(dateFrom)
            params.append(dateTo)
            cursor.execute(query, params)
            for row in cursor:
                result.append((row["Product_number"], row["Product"], row["occorrenze"]))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def getBottomProductsPath(path, dateFrom, dateTo):
        '''
        Estrazione dei tre prodotti che compaiono in numero minore nel cammino debole
        :param path: cammino debole trovato secondo i parametri della ricerca
        :param dateFrom: data di partenza della ricerca
        :param dateTo: data di fine della ricerca
        :return: lista di tuple nella forma (codice prodotto, nome podotto, numero di occorrenze)
        '''
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione Fallita")
        else:
            cursor = cnx.cursor(dictionary=True)

            conditions = []
            params = []


            for i in range(len(path) - 1):
                conditions.append("ds1.Retailer_code = %s AND ds2.Retailer_code = %s")
                params.append(path[i].Retailer_code)
                params.append(path[i + 1].Retailer_code)

            where_pairs = " OR ".join(conditions)

            query = f"""SELECT
                            p.Product_number,
                            p.Product,
                            COUNT(*) AS occorrenze
                        FROM 
                            go_daily_sales ds1,
                            go_daily_sales ds2,
                            go_products p
                        WHERE 
                            ds1.Product_number = ds2.Product_number
                            AND ds1.Product_number = p.Product_number
                            AND ({where_pairs})
                            AND ds1.Date BETWEEN %s AND %s
                            AND ds2.Date BETWEEN %s AND %s

                        GROUP BY 
                            p.Product_number,
                            p.Product
                        ORDER BY 
                            occorrenze ASC
                            LIMIT 3"""

            params.append(dateFrom)
            params.append(dateTo)
            params.append(dateFrom)
            params.append(dateTo)
            cursor.execute(query, params)
            for row in cursor:
                result.append((row["Product_number"], row["Product"], row["occorrenze"]))

            cursor.close()
            cnx.close()
        return result



