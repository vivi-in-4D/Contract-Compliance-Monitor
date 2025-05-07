import pymysql

host = '138.47.148.170'

connection = pymysql.connect(
    host=host,
    user='user', # Your username here
    password='password', # Your password here
    database='contract_compliance', # Your database name here
    )

cursor = connection.cursor()
cursor.execute("SELECT * FROM cui")

rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
connection.close()