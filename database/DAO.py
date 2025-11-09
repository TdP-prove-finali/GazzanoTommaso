from database.DB_connect import DBConnect
from model.Retailer import Retailer


class DAO():
    @staticmethod
    def getAllRetailers(type, productLine, dateFrom, dateTo):
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
                            AND p.Product_line = %s
                            AND ds.Date BETWEEN %s AND %s
                        ORDER BY
                            r.Retailer_code'''
            cursor.execute(query, (type, productLine, dateFrom, dateTo))

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
    def getAllProductLines(rtype):
        '''
        Estrazione dal Database delle ProductLines legate alla tipologia di Retailer
        :param rtype: str
        :return: list(str)
        '''
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione Fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """
                    SELECT DISTINCT p.Product_line AS pl
                    FROM go_retailers r, go_daily_sales ds, go_products p
                    WHERE r.Retailer_code = ds.Retailer_code
                      AND ds.Product_number = p.Product_number
                      AND r.`Type`  = %s
                    ORDER BY pl
                    """

            cursor.execute(query, (rtype, ))

            for row in cursor:
                result.append(row["pl"])

            cursor.close()
            cnx.close()
        return result


