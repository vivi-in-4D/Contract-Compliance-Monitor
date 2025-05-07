from os import path
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7

from keygen import generate_key

'''
What is this program?
This is a program designed to be an import function for 
AES256 encryption and decryption given a...
1. Mode (enc / dec)
2. File path (string) (input file)
3. Password (string) (creates key)
4. IV (32 char hex-string)
'''

# get a string password, string IV
# sample values for testing
PASSWORD = "a_password"
IV = "bb90eb1b8669ba5f65c93e526d413150"
INPUT_FILE = "text.txt"
# INPUT_FILE = "enc_P1cui.txt"
ENC_INPUT_FILE = "enc_text.txt"

def encrypt(cipher: Cipher, payload: bytes) -> bytes:
    '''Encrypts a payload.'''
    enc = cipher.encryptor()
    ciphertext = enc.update(payload) + enc.finalize()
    return ciphertext

def decrypt(cipher: Cipher, payload: bytes) -> bytes:
    '''Decrypts a payload.'''
    dec = cipher.decryptor()
    plaintext = dec.update(payload) + dec.finalize()
    return plaintext

def aes256(mode, input_path, password, iv):
    # Strings
    key_str = generate_key(password)
    iv_str = iv
    # print(key_str)
    # print(iv_str)

    # verify input_path access
    if not path.exists(input_path):
        print(f"Input path is not valid: {input_path}")
        raise ValueError
    # else:
        # print(f"Path: {input_path} exists!")

    # create output path
    if mode == "enc":
        output_path = f"enc_{input_path}"
    else: # mode == dec
        # if enc_ in file path, get rid of it, else add a -1
        try:
            input_spliced = input_path.split("enc_")
            output_path = f"{input_spliced[1]}"
        except:
            input_spliced = input_path.split(".")
            output_path = f"{input_spliced[0]}-1.{input_spliced[1]}"
    
    # byteread
    key_bytes = input_bytes = iv_bytes = None
    try:
        key_bytes = bytearray.fromhex(key_str)
        iv_bytes = bytearray.fromhex(iv_str)
    except ValueError:
        print("Invalid key/iv")
    # print(key_bytes)
    # print(iv_bytes)
    try:
        with open(input_path, "rb") as input_data:
            input_bytes = input_data.read()
    except OSError as exc:
        print("Unable to access input file.")
        raise SystemExit(1) from exc

    # encrypt
    cipher = Cipher(AES(key_bytes), CBC(iv_bytes))
    result = None
    if mode == "enc":
        padder = PKCS7(128).padder()
        input_padded = padder.update(input_bytes) + padder.finalize()
        result = encrypt(cipher, input_padded)
    else: # decrypt
        result_padded = decrypt(cipher, input_bytes)
        try:
            unpadder = PKCS7(128).unpadder()
            result = unpadder.update(result_padded) + unpadder.finalize()
        except ValueError:
            print("Bad padding detected. Keeping padding intact.")
            result = result_padded

    try:
        with open(output_path, "wb") as output_data:
            output_data.write(result)
    except OSError as exc:
        print("Unable to write to output file.")
        raise SystemExit(1) from exc

if __name__ == "__main__":
    print(INPUT_FILE)
    # aes256("enc", INPUT_FILE, PASSWORD, IV)
    aes256("dec", ENC_INPUT_FILE, PASSWORD, IV)
