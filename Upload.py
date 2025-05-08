import pymysql
import sys

ip, iv, cui_name, pre_hash, post_hash, group_name = sys.argv[1:7]

connection = pymysql.connect(
    host=ip,
    user='SFTP', # Your username here
    password='sftp0214', # Your password here
    database='contract_compliance', # Your database name here
    )

cursor = connection.cursor()
# CHECK IF CUI_NAME EXISTS IN THE TABLE
cursor.execute(f"SELECT COUNT(*) FROM `{group_name}_cui` WHERE `cui_name` = '{cui_name}';")
result = cursor.fetchone()

if result[0] > 0:
    # IF CUI_NAME EXISTS, UPDATE THE IV
    query = f"UPDATE `{group_name}_cui` SET `IV` = %s WHERE `cui_name` = %s;"
    cursor.execute(query, (iv, cui_name))
    connection.commit()

else:
    cursor.execute(f"INSERT INTO `{group_name}_cui` (`cui_name`, `IV`) VALUES ('{cui_name}', '{iv}');")
    connection.commit()
cursor.execute(f"INSERT INTO c_hashes (cui_hash) VALUES ('{pre_hash}');")
cursor.execute(f"INSERT INTO c_hashes (cui_hash) VALUES ('{post_hash}');")
connection.commit()

cursor.close()
connection.close()