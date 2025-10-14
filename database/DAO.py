from database.DB_connect import DBConnect

class DAO():
    @staticmethod
    def getAllRetailers():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione Fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = "SELECT * FROM go_retailers"
            cursor.execute(query)

            for row in cursor:
                result.append(row)

            cursor.close()
            cnx.close()
        return result

