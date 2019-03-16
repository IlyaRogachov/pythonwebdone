import MySQLdb

def connection():
    # Edited out actual values
    conn = MySQLdb.connect(host="mysql.default.svc.cluster.local",
                           user="ian",
                           passwd="rognarock",
                           db = "iandb")
    c = conn.cursor()

    return c, conn
