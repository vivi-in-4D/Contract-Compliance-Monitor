import argparse
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

from sys import argv
from os import path
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7



DEFAULT_FILE_SUFFIX_DECRYPT = "_decrypted"
DEFAULT_FILE_SUFFIX_ENCRYPT = "_encrypted"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Window settings
        self.geometry("1080x240")
        self.title("Simple Encrypt")
        
        # Init data
        self.modes = ("Encrypt", "Decrypt")

        # Set up var
        self.mode_selection = tk.StringVar(self)

        # Create Widget
        self.create_widgets()

    def create_widgets(self):
        # Widget padding
        padding = {'padx': 5, 'pady': 5}

        # Mode Label
        mode_label = ttk.Label(self,  text="Select Mode:")
        mode_label.grid(column=0, row=0, sticky=tk.W, **padding)

        # Mode OptionMenu
        mode_option_menu = ttk.OptionMenu(
            self,
            self.mode_selection,
            "Not Selected",
            *self.modes,
            command=self.mode_option_changed)
        mode_option_menu.grid(column=0, row=1, sticky=tk.W, **padding)

        # Mode Output Label
        self.mode_output_label = ttk.Label(self, foreground="red")
        self.mode_output_label.grid(column=0, row=2, sticky=tk.W, **padding)

        # Open Button (key)
        open_key_button = ttk.Button(
            self,
            text="Key file:",
            command=self.select_key
        )
        open_key_button.grid(column=1, row=0, sticky=tk.W, **padding)

        # Output Label (key)
        self.key_output_label = ttk.Label(self, foreground="red")
        self.key_output_label.grid(column=1, row=1, sticky=tk.W, **padding)

        # Open Button (iv)
        open_iv_button = ttk.Button(
            self,
            text="IV file:",
            command=self.select_iv
        )
        open_iv_button.grid(column=1, row=2, sticky=tk.W, **padding)

        # Output Label (iv)
        self.iv_output_label = ttk.Label(self, foreground="red")
        self.iv_output_label.grid(column=1, row=3, sticky=tk.W, **padding)

        # Open Button (input file)
        open_input_button = ttk.Button(
            self,
            text = "Input File:",
            command=self.select_inputfile)    
        open_input_button.grid(column=1, row=4, sticky=tk.W, **padding)

        # Output Label (input file)
        self.inputfile_output_label = ttk.Label(self, foreground="red")
        self.inputfile_output_label.grid(column=1, row=5, sticky=tk.W, **padding)

        # Text Box (Output file):
        self.output_textbox = tk.Text(self, height=1, width=32)
        self.output_textbox.grid(column=2, row=0, sticky=tk.W, **padding)

        # Button (Output file):
        outputfile_button = ttk.Button(
            self,
            text="Submit",
            command = self.show_outputfile 
        )
        outputfile_button.grid(column=2, row=1, sticky=tk.W, **padding)

        # Output Label (Output file)
        self.outputfile_output_label = ttk.Label(self, foreground="red")
        self.outputfile_output_label.grid(column=2, row=2, sticky=tk.W, **padding)

        # Start Button!
        start_button = ttk.Button(
            self,
            text="Start",
            command = self.gui_aes
        )
        start_button.grid(column=3, row=0, sticky=tk.W, **padding)

    def mode_option_changed(self, *args):
        self.mode_output_label["text"] = f"{self.mode_selection.get()}"

    def select_key(self):
        filetypes = (
            ("Text files", "*.dat"),
            ("All files", "*.*")
        )

        filename = fd.askopenfilename(
            title="Open a file",
            initialdir="/",
            filetypes=filetypes
        )

        self.key_output_label["text"] = f"{filename}"

    def select_iv(self):
        filetypes = (
            ("Text files", "*.dat"),
            ("All files", "*.*")
        )

        filename = fd.askopenfilename(
            title="Open a file",
            initialdir="/",
            filetypes=filetypes
        )

        self.iv_output_label["text"] = f"{filename}"

    def select_inputfile(self):
        filetypes = (
            ("Text files", "*.txt"),
            ("Encrypted files", "*.enc"),
            ("All files", "*.*")
        )

        filename = fd.askopenfilename(
            title="Open a file",
            initialdir="/",
            filetypes=filetypes
        )

        self.inputfile_output_label["text"] = f"{filename}"

    def show_outputfile(self):
        self.outputfile_output_label["text"] = f"{self.output_textbox.get('1.0', tk.END)}"

    def gui_aes(self):
        mode = self.mode_output_label["text"]
        key_path = self.key_output_label["text"]
        iv_path = self.iv_output_label["text"]
        input_path = self.inputfile_output_label["text"]
        output_path = self.outputfile_output_label["text"].strip("\n")
        aes(mode, key_path, iv_path, input_path, output_path, gui=True)


def aes(mode, key_path, iv_path, input_path, output_path, gui=False):
    try:
        assert mode in ("Encrypt", "Decrypt")
        enc = mode == "Encrypt"

        # Validate file paths
        for file_path in [key_path, iv_path, input_path]:
            if not path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")

        restricted_characters = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
        if any(char in output_path for char in restricted_characters):
            raise ValueError("Invalid characters in output path")

        # Read key, IV, and input file
        with open(key_path, "r", encoding="utf-8") as key_data:
            key_bytes = bytearray.fromhex(key_data.read().strip())
        with open(iv_path, "r", encoding="utf-8") as iv_data:
            iv_bytes = bytearray.fromhex(iv_data.read().strip())
        with open(input_path, "rb") as input_data:
            input_bytes = input_data.read()

        # Perform encryption or decryption
        cipher = Cipher(AES(key_bytes), CBC(iv_bytes))
        if enc:
            padder = PKCS7(128).padder()
            input_padded = padder.update(input_bytes) + padder.finalize()
            result = cipher.encryptor().update(input_padded) + cipher.encryptor().finalize()
        else:
            result_padded = cipher.decryptor().update(input_bytes) + cipher.decryptor().finalize()
            try:
                unpadder = PKCS7(128).unpadder()
                result = unpadder.update(result_padded) + unpadder.finalize()
            except ValueError as e:
                raise ValueError("Decryption failed: Invalid padding or corrupted data.") from e

        # Write output
        with open(output_path, "wb") as output_data:
            output_data.write(result)

        if gui:
            showinfo(
                title="Success!",
                message=f"Mode: {mode}\n"
                        f"Key: {key_path}\n"
                        f"IV: {iv_path}\n"
                        f"Input File: {input_path}\n"
                        f"Output File: {output_path}\n"
                        f"{mode}ion successful, saved to {output_path}"
            )
        else:
            print(f"{mode}ion successful, saved to {output_path}")

    except Exception as e:
        if gui:
            showinfo(title="Error", message=str(e))
        else:
            print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Encrypt CLI/GUI Tool")
    parser.add_argument("--cli", action="store_true", help="Use CLI mode")
    parser.add_argument("--mode", choices=["Encrypt", "Decrypt"], help="Encrypt or Decrypt")
    parser.add_argument("--key", help="Path to key file")
    parser.add_argument("--iv", help="Path to IV file")
    parser.add_argument("--input", nargs='+', help="Path(s) to input file(s)")
    parser.add_argument("--output", nargs='*', help="Path(s) to output file(s) (optional, defaults to input-based names)")
    args = parser.parse_args()

    if args.cli:
        if not all([args.mode, args.key, args.iv, args.input]):
            print("Error: Arguments (--mode, --key, --iv, --input) are required in CLI mode.")
            exit

        # Ensure output file list matches input file list
        output_files = args.output if args.output else []
        for i, input_file in enumerate(args.input):
            if i < len(output_files):
                output_file = output_files[i]
            else:
                # Generate default output file name
                base_name, ext = path.splitext(input_file)
                suffix = DEFAULT_FILE_SUFFIX_ENCRYPT if args.mode == "Encrypt" else DEFAULT_FILE_SUFFIX_DECRYPT
                output_file = f"{base_name}{suffix}{ext}"

            print(f"Processing: {input_file} -> {output_file}")
            aes(args.mode, args.key, args.iv, input_file, output_file)
    else:
        app = App()
        app.mainloop()