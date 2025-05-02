import argparse
import random

ACCEPTABLE_CHARS = "0123456789abcdef"

def generate_iv() -> str:
    return ''.join(random.choices(ACCEPTABLE_CHARS, k=32))

def main():
    parser = argparse.ArgumentParser(description="Generate random AES IVs.")
    parser.add_argument("count", type=int, help="Number of IVs to generate")
    parser.add_argument("--prefix", default="IV", help="Filename prefix for IVs")
    args = parser.parse_args()

    for i in range(1, args.count + 1):
        iv = generate_iv()
        filename = f"{args.prefix}{i}.dat"
        with open(filename, "w") as f:
            f.write(iv)
        print(f"IV written to {filename}")

if __name__ == "__main__":
    main()