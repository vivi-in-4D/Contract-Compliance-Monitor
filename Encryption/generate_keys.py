import random

# generate key and iv files
acceptable_char = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
# key files are 64 length alphanumeric, iv files are 32 length alphanumeric
raw_resp = input("Please enter the number of key and IV files you wish to generate: ")
key_num = int(raw_resp)
i = 0
keys = []
ivs = []
while (i < key_num):
    # generate a key
    key = ""
    j = 0
    while (j < 64):
        key += random.choice(acceptable_char)
        j += 1
    # generate an iv
    iv = ""
    j = 0
    while (j < 32):
        iv += random.choice(acceptable_char)
        j += 1
    keys.append(key)
    ivs.append(iv)
    i += 1

i = 1
for key in keys:
    # print(f"Key{i}: {key}")
    filename = f"Key{i}.dat"
    with open(filename, "w") as file:
        file.write(key)
    i += 1
i = 1
for iv in ivs:
    # print(f"IV{i}: {iv}")
    filename = f"IV{i}.dat"
    with open(filename, "w") as file:
        file.write(iv)
    i += 1
