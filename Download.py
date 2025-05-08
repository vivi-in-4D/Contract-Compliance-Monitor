import pymysql
import sys

ip, group_name = sys.argv[1:3]

connection = pymysql.connect(
    host=ip,
    user='SFTP',  # Your username here
    password='sftp0214',  # Your password here
    database='contract_compliance',  # Your database name here
)

cursor = connection.cursor()

cursor.execute(f"SELECT 'pass_hash' FROM 'pass_hashes' WHERE 'group_name' = '{group_name,}'")

result = cursor.fetchone()

pass_hash = result[0]
print(pass_hash)

cursor.close()
connection.close()
