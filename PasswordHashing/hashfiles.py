import hashlib
import os

def sha3_sum(filename):
    # read in 64kb chunks, so we don't eat all the memory in the system
    BUFFER_SIZE = 65536
    # sha1 = hashlib.sha1()
    sha3 = hashlib.sha3_256()
    with open(filename, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha3.update(data)
    return sha3.hexdigest()
    
def export_hashes(hashlist):
    with open('testhashes.txt', 'w') as file:
        for line in hashlist:
            file.writelines(line + "\n") 

directory_name = os.path.dirname(__file__)
sha3_hashlist = []

for file in os.listdir(directory_name):
    sha3_hash = sha3_sum(file)
    sha3_hashlist.append(f"File: {file} SHA3: {sha3_hash}")
    print(f"File: {file} SHA3: {sha3_hash}")
    
export_hashes(sha3_hashlist)
print("Hashes have been exported to testdata.txt")
