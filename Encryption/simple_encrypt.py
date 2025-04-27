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

# Our tk version is 8.6.15
'''
Goal: create a GUI that uses the functionality of the aes program
Mode (OptionMenu): Encrypt/Decrypt
Select (AskOpen): Key
Select (AskOpen): IV
Select (AskOpen): Input file
Text (Textbox): Output file
Button: Start
'''
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Window settings
        self.geometry("1080x240")
        self.title("Simple Encrypt")
        '''window_width = 300
        # window_height = 200
        # screen_width = self.winfo_screenwidth()
        # screen_height = self.winfo_screenheight()
        # center_x = int(screen_width/2 - window_width/2)
        # center_y = int(screen_height/2 - window_height/2)
        # self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")'''
        
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
            command = self.aes
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
        self.outputfile_output_label["text"] = f"{self.output_textbox.get("1.0", tk.END)}"

    def encrypt(self, cipher: Cipher, payload: bytes) -> bytes:
        # Encrypt Payload
        enc = cipher.encryptor()
        ciphertext = enc.update(payload) + enc.finalize()
        return ciphertext
    
    def decrypt(self, cipher: Cipher, payload: bytes) -> bytes:
        # Decrypt Payload
        dec = cipher.decryptor()
        plaintext = dec.update(payload) + dec.finalize()
        return plaintext

    def aes(self):
        try:
            # get operation
            mode = self.mode_output_label["text"]
            assert "Encrypt" in mode or "Decrypt" in mode
            if (mode == "Encrypt"):
                # print("Using Encryption!")
                enc = True
            else:
                # print("Using Decryption")
                enc = False

            # get key
            key_path = self.key_output_label["text"]
            # make sure key_path exists
            if not path.exists(key_path):
                print(f"Key path is not valid: {key_path}")
                raise ValueError

            # get iv
            iv_path = self.iv_output_label["text"]
            # make sure iv_path exists
            if not path.exists(iv_path):
                print(f"IV path is not valid: {iv_path}")
                raise ValueError

            # get input file
            input_path = self.inputfile_output_label["text"]
            # make sure input_path exists
            if not path.exists(input_path):
                print(f"Input path is not valid: {input_path}")
                raise ValueError

            output_path = self.outputfile_output_label["text"]
            # make sure output_path exists and legal
            restricted_characters = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
            for char in restricted_characters:
                if (char in output_path):
                    print("Invalid Text given for output path")
                    raise ValueError

        except (ValueError, AssertionError) as exc:
            print("Error detected, closing program")
            raise SystemExit(1) from exc
        
        # read in the key
        # print("Reading in the key...")
        key_bytes = input_bytes = iv_bytes = None
        try:
            with open(key_path, "r", encoding="utf-8") as key_data:
                key_str = key_data.read()
            # print(f"Key: {key_str}")
        except OSError as exc:
            print("Unable to access key file.")
            raise SystemExit(1) from exc
        try:
            with open(iv_path, "r", encoding="utf-8") as iv_data:
                iv_str = iv_data.read()
            # print(f"IV: {iv_str}")
        except OSError as exc:
            print("Unable to access IV file.")
            raise SystemExit(1) from exc
        try:
            with open(input_path, "rb") as input_data:
                input_bytes = input_data.read()
            # print(f"Input: {input_bytes}")
        except OSError as exc:
            print("Unable to access input file.")
            raise SystemExit(1) from exc
        
        try:
            key_bytes = bytearray.fromhex(key_str)
            iv_bytes = bytearray.fromhex(iv_str)
        except ValueError:
            print("Invalid key/iv")

        # encrypt
        cipher = Cipher(AES(key_bytes), CBC(iv_bytes))
        result = None
        if enc:
            padder = PKCS7(128).padder()
            input_padded = padder.update(input_bytes) + padder.finalize()
            result = self.encrypt(cipher, input_padded)
        else:
            result_padded = self.decrypt(cipher, input_bytes)
            try:
                unpadder = PKCS7(128).unpadder()
                result = unpadder.update(result_padded) + unpadder.finalize()
            except ValueError:
                print("Bad padding detected. Keeping padding intact.")
                result = result_padded

        # Write output to file
        output_path = output_path.strip("\n") # STRIP THE NEWLINE
        # print(f"Output: {output_path}, Type: {type(output_path)}")
        try:
            # output_path = str(output_path)
            with open(output_path, "wb") as output_data:
                output_data.write(result)
            showinfo(
                title = "Success!",
                message = f"Mode: {mode}\n" \
                f"Key: {key_path}\n" \
                f"IV: {iv_path}\n" \
                f"Input File: {input_path}\n" \
                f"Output File: {output_path}\n" \
                f"{mode}ion successful, saved to {output_path}" 
            )
        except OSError as exc:
            print("Unable to write to output file.")
            raise SystemExit(1) from exc


if __name__ == "__main__":
    app = App()
    app.mainloop()
