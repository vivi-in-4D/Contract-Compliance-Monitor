import pymysql
import sys
if len(sys.argv) != 7:
    print("Usage: python DatabaseTest.py <IP> <IV> <CUI_NAME> <PRE_HASH> <POST_HASH> <GROUP_NAME>")
    sys.exit(1)

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
    cursor.execute(f"UPDATE `{group_name}_cui` SET `IV` = '{iv}' WHERE `cui_name` = '{cui_name}';")

else:
    #INSERTS NEW CUI INTO THE DATABASE
    cursor.execute(f"INSERT INTO `{group_name}_cui` (`cui_name`, `IV`) VALUES ('{cui_name}', '{iv}');")
    
cursor.execute(f"INSERT INTO `c_hashes` (`cui_hash`) VALUES ('{pre_hash}');")
cursor.execute(f"INSERT INTO `c_hashes` (`cui_hash`) VALUES ('{post_hash}');")

cursor.close()
connection.close()