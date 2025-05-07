#===IMPORTS===#

import tkinter as tk
import socket as sc
import re
import os

#===GLOBALS===#

window = tk.Tk()
window.title("PROXY SERVER CONFIGURATION")
window.geometry("900x600")
window.resizable(False, False)

def IP_search():
    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if line.strip().startswith("Listen"):
                return line.strip().split()[1]

    except Exception as e:
        print(f"Error finding IP: {e}")

CURRENT_IP = IP_search()

label_proxy_ip = tk.Label(window, text=f"Your Current Proxy IP is {CURRENT_IP}:")
button_sync_ip = tk.Button(window, text="Sync IP")
button_reset_ip = tk.Button(window, text="Reset IP")
button_add_block = tk.Button(window, text="Add ProxyBlock")
button_remove_block = tk.Button(window, text="Remove ProxyBlock")
button_add_ip = tk.Button(window, text="Add IP")
button_remove_ip = tk.Button(window, text="Remove IP")
button_refresh_webtraffic = tk.Button(window, text="Refresh")
query_blacklist_text = tk.Text(window, height=10, width=50, state = tk.DISABLED)
query_whitelist_text = tk.Text(window, height=10, width=50, state = tk.DISABLED)
query_webtraffic_text = tk.Text(window, height=10, width=100, state=tk.DISABLED)

entry_block = tk.Entry(window)
entry_ip = tk.Entry(window)

#===FUNCTIONS===#


def on_button_click_sync_ip():
    s = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    print("Your local IP is: " + local_ip)

    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        with open(proxy_conf_path, "w") as file:
            for line in lines:
                if line.strip().startswith("Listen"):
                    file.write(f"Listen {local_ip}:8080\n")
                else:
                    file.write(line)

        print(f"Updated Listen directive to: {local_ip}")
    except Exception as e:
        print(f"Error updating Listen directive: {e}")

    label_proxy_ip.config(text="Your Current Proxy IP is: " +  local_ip + ":8080")

def on_button_click_reset_ip():
    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        with open(proxy_conf_path, "w") as file:
            for line in lines:
                if line.strip().startswith("Listen"):
                    file.write("Listen 0.0.0.0:80\n")
                else:
                    file.write(line)

        print("Updated Listen directive to: 0.0.0.0:80")
    except Exception as e:
        print(f"Error updating Listen directive: {e}")
    
    label_proxy_ip.config(text="Your Proxy IP has been reset to 0.0.0.0:80")

def on_button_click_add_block():
    new_block = entry_block.get()
    if not new_block:
        print("No domain provided to block.")
        return

    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        # Check if the ProxyBlock already exists
        if any(f"ProxyBlock .{new_block}." in line for line in lines):
            print(f"ProxyBlock {new_block} already exists in the configuration.")
            return

        with open(proxy_conf_path, "a") as file:
            file.write(f"  ProxyBlock .{new_block}.\n")

        query_blacklist()
        print(f"Added ProxyBlock for: {new_block}")
    except Exception as e:
        print(f"Error adding ProxyBlock: {e}")

def on_button_click_remove_block():
    remove_block = entry_block.get()
    if not remove_block:
        print("No domain provided to unblock.")
        return

    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        with open(proxy_conf_path, "w") as file:
            for line in lines:
                if line.strip() != f"ProxyBlock .{remove_block}.":
                    file.write(line)
        query_blacklist()

        print(f"Removed ProxyBlock for: {remove_block}")
    except Exception as e:
        print(f"Error removing ProxyBlock: {e}")

def on_button_click_add_IP():
    new_ip = entry_ip.get()
    if not new_ip:
        print("No IP address provided.")
        return

    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        if any(f"Allow from {new_ip}" in line for line in lines):
            print(f"IP {new_ip} already exists in the configuration.")
            return

        with open(proxy_conf_path, "w") as file:
            inside_proxy = False
            proxy_lines = []  # Temporary storage for lines inside the <Proxy *> block

            for line in lines:
                if line.strip() == "<Proxy *>":
                    inside_proxy = True
                    proxy_lines.append(line)
                elif inside_proxy and line.strip() == "</Proxy>":
                    # Add the new IP after the last "Allow from" line
                    for proxy_line in proxy_lines:
                        file.write(proxy_line)
                    file.write(f"    Allow from {new_ip}\n")
                    file.write(line)
                    inside_proxy = False
                    proxyk_lines = []  # Clear temporary storage
                elif inside_proxy:
                    proxy_lines.append(line)
                else:
                    file.write(line)

        query_whitelist()
        print(f"Added IP: {new_ip}")
    except Exception as e:
        print(f"Error adding IP: {e}")

    

def on_button_click_remove_IP():
    remove_ip = entry_ip.get()
    if not remove_ip:
        print("No IP provided to whitelist.")
        return

    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        with open(proxy_conf_path, "w") as file:
            for line in lines:
                if line.strip() != f"Allow from {remove_ip}":
                    file.write(line)
        query_whitelist()

        print(f"Removed IP for: {remove_ip}")
    except Exception as e:
        print(f"Error removing IP: {e}")
    
def webtraffic_refresh():
    query_webtraffic()
    
    

def query_blacklist():
    query_blacklist_text.config(state=tk.NORMAL)
    query_blacklist_text.delete(1.0, tk.END)
    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if line.strip().startswith("ProxyBlock"):
                proxy_blocks = [line.strip().replace("ProxyBlock .", "").replace(".", "") for line in lines if line.strip().startswith("ProxyBlock")]
        query_blacklist_text.insert(tk.END, "\n".join(proxy_blocks))
        query_blacklist_text.config(state=tk.DISABLED)
    except Exception as e:
        print(f"Error querying ProxyBlocks: {e}")

def query_whitelist():
    query_whitelist_text.config(state=tk.NORMAL)
    query_whitelist_text.delete(1.0, tk.END)
    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        proxy_conf_path = os.path.join(xampp_path, "apache", "conf", "extra", "httpd-proxy.conf")

        if not os.path.exists(proxy_conf_path):
            raise FileNotFoundError(f"File not found: {proxy_conf_path}")

        with open(proxy_conf_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if line.strip().startswith("Allow"):
                allowed_ip = [line.strip().replace("Allow from ", "") for line in lines if line.strip().startswith("Allow from")]
        query_whitelist_text.insert(tk.END, "\n".join(allowed_ip))
        query_whitelist_text.config(state=tk.DISABLED)
    except Exception as e:
        print(f"Error querying ProxyBlocks: {e}")

def query_webtraffic():
    query_webtraffic_text.config(state=tk.NORMAL)
    query_webtraffic_text.delete(1.0, tk.END)
    try:
        xampp_path = None
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            potential_path = f"{drive}:\\xampp"
            if os.path.exists(potential_path):
                xampp_path = potential_path
                break

        if not xampp_path:
            raise FileNotFoundError("XAMPP installation directory not found.")

        log_path = os.path.join(xampp_path, "apache", "logs", "access.log")

        if not os.path.exists(log_path):
            raise FileNotFoundError(f"File not found: {log_path}")

        with open(log_path, "r") as file:
            lines = file.readlines()[::-1]  

        # Regular expression to parse log lines
        log_pattern = re.compile(
            r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<timestamp>[^\]]+)\] "(?:GET|POST|CONNECT) (?P<destination>[^\s:]+)'
        )

        # Process each line
        for line in lines:
            match = log_pattern.search(line)
            if match:
                ip = match.group('ip')
                timestamp = match.group('timestamp')
                destination = match.group('destination')
                query_webtraffic_text.insert(tk.END, f"{ip} [{timestamp}] => {destination}\n")

        query_webtraffic_text.config(state=tk.DISABLED)

    except Exception as e:
        print(f"Error querying web traffic: {e}")
    
    window.after(5000, query_webtraffic)

def confirmation_popup(callback_yes, callback_no=None):
    popup = tk.Toplevel(window)
    popup.title("Confirmation")
    label = tk.Label(popup, text="Are you sure you want to proceed?")
    label.pack()

    def on_yes():
        if callback_yes:
            callback_yes()
        popup.destroy()

    def on_no():
        if callback_no:
            callback_no()
        popup.destroy()

    button_yes = tk.Button(popup, text=" Yes ", command=on_yes)
    button_yes.pack(padx=100)

    button_no = tk.Button(popup, text=" No ", command=on_no)
    button_no.pack(padx=100)

    window.wait_window(popup)

def wrap_with_confirmation(callback):
    def wrapped_callback():
        confirmation_popup(callback_yes=callback)
    return wrapped_callback

#===BUTTON_CONFIGS===#

button_sync_ip.config(command=wrap_with_confirmation(on_button_click_sync_ip))
button_reset_ip.config(command=wrap_with_confirmation(on_button_click_reset_ip))
button_add_block.config(command=wrap_with_confirmation(on_button_click_add_block))
button_remove_block.config(command=wrap_with_confirmation(on_button_click_remove_block))
button_add_ip.config(command=wrap_with_confirmation(on_button_click_add_IP))
button_remove_ip.config(command=wrap_with_confirmation(on_button_click_remove_IP))
button_refresh_webtraffic.config(command=query_webtraffic)


#===GUI SETUP===#

label_proxy_ip.grid(row=0, column=2, columnspan=4, rowspan=2, sticky="w")
button_sync_ip.grid(row=0, column=1, pady=5, sticky="nsew")
button_reset_ip.grid(row=1, column=1, sticky="nsew")

tk.Label(window, text="Add/Remove ProxyBlock (e.g., youtube):").grid(row=7, column=0, columnspan=2, pady=5)
entry_block.grid(row=8, column=1, columnspan=1, rowspan=2, sticky="ew")
button_add_block.grid(row=8, column=0, sticky="nsew", padx=5, pady=5)
button_remove_block.grid(row=9, column=0, sticky="nsew", padx=5, pady=5)

tk.Label(window, text="Blacklisted Domains:").grid(row=10, column=0, columnspan=2, pady=5)
query_blacklist_text.grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

tk.Label(window, text="Add IP (e.g., 127.0.0.1):").grid(row=7, column=4, columnspan=2, pady=5)
entry_ip.grid(row=8, column=5, columnspan=2, rowspan=2, sticky="ew")
button_add_ip.grid(row=8, column=4, sticky="nsew", padx=5, pady=5)
button_remove_ip.grid(row=9, column=4, sticky="nsew", padx=5, pady=5)

tk.Label(window, text="Whitelisted Domains:").grid(row=10, column=4, columnspan=2, pady=5)
query_whitelist_text.grid(row=11, column=4, columnspan=2, padx=5, pady=5, sticky="nsew")

tk.Label(window, text="Web Traffic:").grid(row=18, column=1, columnspan=1, pady=5, sticky="e")
query_webtraffic_text.grid(row=19, column=0, columnspan=8, padx=5, pady=5, sticky="nsew")
button_refresh_webtraffic.grid(row=18, column=2, columnspan=2, padx=5, pady=5, sticky="nsew")

#===MAIN===#

query_blacklist()
query_whitelist()
query_webtraffic()

window.mainloop()