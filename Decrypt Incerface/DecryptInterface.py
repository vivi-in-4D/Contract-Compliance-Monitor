#===IMPORTS===#

import tkinter as tk
from tkinter import messagebox
import socket as sc
import cryptography

#===GLOABLS===#

fail_counter = 0

window = tk.Tk()
window.title("Decrypt Interface Login")
window.geometry("900x600")
window.resizable(False, False)

button_login = tk.Button(window, text="Login", width=10, height=2, bg="gray", fg="white")
button_close = tk.Button(window, text="Close", width=10, height=2, bg="gray", fg="white")

entry_username = tk.Entry(window, width=20, bg="white", fg="black")
entry_password = tk.Entry(window, width=20, bg="white", fg="black", show="*")

#===FUNCTIONS===#

def on_click_login():
    password = entry_password.get()
    username = entry_username.get()

    # Check if username and password are valid "THIS NEEDS TO BE CHANGED"
    if username == "username" and password == "password":
        login_successful()
        
    else:
        global fail_counter
        login_failed()
        fail_counter += 1
        if fail_counter >= 3:
            print("Too many failed attempts")
            window.destroy()
            tk.messagebox.showerror("Too many attempts", "You have been locked out due to too many failed login attempts.")

def login_successful():
    print("Login successful")
    window.withdraw()
    generate_query_window()

def login_failed():
    tk.messagebox.showerror("Login Failed", "Invalid username or password")
    entry_username.delete(0, tk.END)
    print("Login failed")

def generate_query_window():
    query_window = tk.Toplevel(window)
    query_window.title("Decrypt Interface")

    button_close = tk.Button(query_window, text="Close", width=10, height=2, bg="gray", fg="white", command=window.destroy)
    button_close.grid(row=0, column=0, padx=10, pady=10)

    file_listbox = tk.Listbox(query_window, width=50, height=15)
    file_listbox.grid(row=1, column=0, padx=10, pady=10)

    # Example file names - add function to fetch actual file names from database
    files = ["file1.txt", "file2.pdf", "file3.docx"]

    for file in files:
        file_listbox.insert(tk.END, file)

    def download_file():
        selected_file = file_listbox.get(tk.ACTIVE)
        if selected_file:
            tk.messagebox.showinfo("Download", f"Downloading {selected_file}")
        else:
            tk.messagebox.showwarning("Please select a file to download.")

    button_download = tk.Button(query_window, text="Download", width=10, height=2, bg="gray", fg="white", command=download_file)
    button_download.grid(row=2, column=0, padx=10, pady=10)

    #THIS FUNCTION NEEDS TO BE IMPLEMENTED
def file_decryptor(file):
    pass

#===BUTTON CONFIGS===#

button_login.config(command=on_click_login)
button_close.config(command=window.quit)

#===GUI SETUP===#

button_login.grid(row=0, column=0, padx=10, pady=10)
entry_username.grid(row=0, column=1, padx=10, pady=10)
entry_password.grid(row=0, column=2, padx=10, pady=10)

#===MAIN===#

window.mainloop()