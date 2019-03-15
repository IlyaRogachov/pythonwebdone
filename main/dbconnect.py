import MySQLdb

def connection():
    # Edited out actual values
    conn = MySQLdb.connect(host="localhost",
                           user="ian",
                           passwd="rognarock",
                           db = "iandb")
    c = conn.cursor()

    return c, conn
