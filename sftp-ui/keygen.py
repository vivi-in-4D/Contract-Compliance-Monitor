import hashlib
import argparse

def generate_key(passphrase: str) -> str:
    # Generate 256-bit key (64 hex characters) from passphrase
    hash_obj = hashlib.sha256(passphrase.encode())
    return hash_obj.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Generate AES-256 key from passphrase.")
    parser.add_argument("passphrase", help="Passphrase to derive the key from")
    parser.add_argument("--output", default="Key.dat", help="Output filename for key")
    args = parser.parse_args()

    key = generate_key(args.passphrase)
    print(key)

if __name__ == "__main__":
    main()