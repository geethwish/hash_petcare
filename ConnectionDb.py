
import mysql.connector


def connection():
    cnx = mysql.connector.connect(user='root',
                                  database='hash_pet_care')
    c = cnx.cursor(buffered=True)
    return c, cnx
