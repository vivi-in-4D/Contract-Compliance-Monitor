#===IMPORTS===#

import tkinter as tk
from tkinter import messagebox
import pymysql

#===GLOABLS===#

fail_counter = 0

# Need to add a way to dynamically search for the host IP

window = tk.Tk()
window.title("Decrypt Interface Login")
window.geometry("450x100")
window.resizable(False, False)

button_login = tk.Button(window, text="Login", width=10, height=2, bg="gray", fg="white")

entry_username = tk.Entry(window, width=20, bg="white", fg="black")
entry_password = tk.Entry(window, width=20, bg="white", fg="black", show="*")

#===FUNCTIONS===#

def on_click_login():
    password = entry_password.get()
    username = entry_username.get()

    try:
        connection = pymysql.connect(
            host="138.47.148.170",
            user=username,
            password=password,
            database="contract_compliance",
        )
        login_successful(username, password)
        connection.close()

    except pymysql.MySQLError as e:
        global fail_counter
        login_failed()
        fail_counter += 1
        if fail_counter >= 3:
            window.destroy()
            tk.messagebox.showerror("Too many attempts", "You have been locked out due to too many failed login attempts.")

def login_successful(username, password):
    window.withdraw()
    
    cui_files = []
    hashes_files = []

    connection = pymysql.connect(
            host="138.47.148.170",
            user=username,
            password=password,
            database="contract_compliance",
        )
    # GRABS ALL TABLES FOR USER IN THE DATABASE
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        cursor.execute(f"SELECT * FROM {table[0]}")
        if 'cui' in table[0]:
            cui_files = cursor.fetchall()

        elif 'hash' in table[0]:
            hashes_files = cursor.fetchall()


    connection.close()
    generate_query_window(cui_files, hashes_files, password)

def login_failed():
    tk.messagebox.showerror("Login Failed", "Invalid username or password")
    entry_username.delete(0, tk.END)

def generate_query_window(cui_files, hashes_files, password):
    query_window = tk.Toplevel(window)
    query_window.title("Decrypt Interface")

    query_window.protocol("WM_DELETE_WINDOW", window.quit)
   
    file_listbox = tk.Listbox(query_window, width=50, height=15)
    file_listbox.grid(row=1, column=0, padx=10, pady=10)

    with open("hashdatabase.txt", "w") as f:
        for hashes in hashes_files:
            f.write(f"{hashes[0]}\n")

    
    for file in cui_files:
        file_listbox.insert(tk.END, file[0])

    def download_file():
        selected_file = file_listbox.get(tk.ACTIVE)
        if selected_file:
            tk.messagebox.showinfo("Download", f"Downloading {selected_file}")
            for file in cui_files:
                if selected_file == file[0]:
                    with open(f"{file[0]}_IV", "w") as f:
                        f.write(f"{file[1]}".strip(" "))
                    tk.messagebox.showinfo("Download", f"{selected_file} downloaded successfully.")
                    file_decryptor(file[1], password)
                    break

            
        else:
            tk.messagebox.showwarning("Please select a file to download.")

    button_download = tk.Button(query_window, text="Download", width=10, height=2, bg="gray", fg="white", command=download_file)
    button_download.grid(row=2, column=0, padx=10, pady=10)

    #THIS FUNCTION NEEDS TO BE IMPLEMENTED
def file_decryptor(IV, password):
    pass


#===BUTTON CONFIGS===#

button_login.config(command=on_click_login)

#===GUI SETUP===#

button_login.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
tk.Label(window, text="Username:").grid(row=0, column=1, padx=10, pady=3, sticky="s")
tk.Label(window, text="Password:").grid(row=0, column=2, padx=10, pady=3, sticky="s")
entry_username.grid(row=1, column=1, rowspan=2, padx=10, pady=3, sticky="n")
entry_password.grid(row=1, column=2, rowspan=2, padx=10, pady=3, sticky="n")

#===MAIN===#

window.mainloop()