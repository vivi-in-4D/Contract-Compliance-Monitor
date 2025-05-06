import time
import logging
import os
import hashlib
import platform
from watchdog.observers import Observer
from watchdog.events import *

'''
Testing Data (Home Directory)
fastest time: 729s on windows (slow)
fastest time: 1.0s on linux (fast)
'''
# Get directory path and path of CUI
# 0 = Home Directory, 
# 1 = Parent Directory, 
# 2 = Parent Parent Directory
# 3 = Root Directory 
MODE = 0
DEBUG_MODE = True
SKIP_SETUP = False
CUI_LOG_PATH = "cui_changes.log"
ALL_LOG_PATH = "all_changes.log"

class cuiHandler(PatternMatchingEventHandler):
    def on_modified(self, event):
        # log
        self.logging_event(event.src_path, "Modified")

    def on_created(self, event):
        self.check_cui(event.src_path)
        # log
        self.logging_event(event.src_path, "Created")

    def on_deleted(self, event):
        # log
        self.logging_event(event.src_path, "Deleted")

    def on_moved(self, event):
        # check to see if destination is in ignore and remove if so (solves undo problem)
        if event.dest_path in self.ignore_patterns:
            self.ignore_patterns.remove(event.dest_path)
        self.logging_event(event.src_path, "Moved", dest_path=event.dest_path)
        # Print patterns for testing purposes
        # if DEBUG_MODE:
            # print(f"Patterns: {self.patterns}")
            # print(f"Ignored: {self.ignore_patterns}")

    # Control Logging
    def logging_event(self, src_path, action, dest_path = None):
        if (".vscode" not in src_path) or ("AppData" not in src_path): # likely not false positive
            if DEBUG_MODE:
                print("[logging_setup] NOT APPDATA/vscode file")
            # log action
            if action == "Moved":
                cui_logger.info(f"{action}: {src_path} to {dest_path}")
            else:
                cui_logger.info(f"{action}: {src_path}")
        if action == "Moved":
            mass_logger.info(f"{action}: {src_path} to {dest_path}")
        else:
            mass_logger.info(f"{action}: {src_path}")
    
    # Into Non-watchdog functions 
    def setup_cui(self, dir_path):
        if DEBUG_MODE:
            print(f"[setup_cui] Path: {dir_path}")
        # some folders are not accessible by the program (Application Data)
        # as a result, use try/except whenever we use "os.listdir(dir_path)"
        try:
            if DEBUG_MODE:
                print(f"[setup_cui] Items in path: {os.listdir(dir_path)}")
            for file in os.listdir(dir_path):
                # fix pathing issue
                if (self.client_os == "Windows"):
                    file_path = dir_path + "\\" + file # may only work in windows
                else: # Linux os
                    file_path = dir_path + "/" + file
                if DEBUG_MODE:
                    print(f"[setup_cui] File: {os.path.abspath(file_path)}")
                # check if folder -> if folder, check inside
                if (os.path.isdir(file_path)):
                    # if folder, check inside
                    if DEBUG_MODE:
                        print(f"[setup_cui] {file} is directory")
                        print(f"[setup_cui] {file_path} is directory path")
                    self.setup_cui(file_path) # recursion to cover folders in folders
                else:
                    self.check_cui(os.path.abspath(file_path))
        except:
            if DEBUG_MODE:
                print("[setup_cui] This folder is not accessible.")
            pass
        # if DEBUG_MODE:
        #     print(f"Patterns: {self.patterns}")
        #     print(f"Ignored: {self.ignore_patterns}")

    def check_cui(self, filename):
        cui_status = self.compare_hash(filename)
        if DEBUG_MODE:
            print(f"[check_cui] File: {filename}, CUI: {cui_status}")
        if (cui_status == False):
            # under the new scheme, add anything not cui to ignore
            self.ignore_patterns.append(filename)
    
    def sha3_sum(self, filename):
        # read in 64kb chunks, so we don't eat all the memory in the system
        BUFFER_SIZE = 65536
        sha3 = hashlib.sha3_256()
        try:
            with open(filename, "rb") as f:
                while True:
                    data = f.read(BUFFER_SIZE)
                    if not data:
                        break
                    sha3.update(data)
        except:
            if DEBUG_MODE:
                print(f"[sha3sum] Error with hashing file: {filename}")
            return False
        if DEBUG_MODE:
                print(f"[sha3sum] File: {filename}, Hash: {sha3.hexdigest()}")
        return sha3.hexdigest()
    
    def compare_hash(self, filename):
        sha3_hash = self.sha3_sum(filename)
        # This is where you put hashes of all CUI
        if sha3_hash in self.hashes:
            return True
        else:
            return False
        
    def import_hashes():
        cui_hashes = []
        with open('hashdatabase.txt', 'r') as f:
            # create an array and return it
            for line in f:
                cui_hashes.append(line.strip("\n"))
            return cui_hashes

    # Important: Controls filter!
    patterns = ["*"]
    ignore_patterns = [CUI_LOG_PATH, ALL_LOG_PATH]
    ignore_directories = True
    hashes = import_hashes()
    client_os = platform.system()

def monitor_setup(dir_path):
    observer.schedule(event_handler, dir_path, recursive = True)
    start_time = time.time()
    if not SKIP_SETUP:
        cuiHandler().setup_cui(dir_path)
    stop_time = time.time()
    elasped_time = stop_time - start_time
    print(f"[monitor_setup] The setup process took {elasped_time} seconds to complete.")

def setup_logger(logger_name, file_name, level=logging.INFO):
    log = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    fileHandler = logging.FileHandler(file_name, mode='a')
    fileHandler.setFormatter(formatter)

    log.setLevel(level)
    log.addHandler(fileHandler)

# Set up the CUI monitor
if __name__ == "__main__":
    # setup log files
    setup_logger("cui_log", CUI_LOG_PATH)
    setup_logger("mass_log", ALL_LOG_PATH)
    cui_logger = logging.getLogger("cui_log")
    mass_logger = logging.getLogger("mass_log")

    home_path = os.path.expanduser("~")
    directory_name = os.path.dirname(__file__)
    parent_directory = os.path.dirname(directory_name)
    root_path = os.path.abspath('.').split(os.path.sep)[0]+os.path.sep # gets root path

    # Monitoring setup
    event_handler = cuiHandler()
    observer = Observer()
    if (MODE == 0):
        monitor_setup(home_path)
    elif (MODE == 1):
        monitor_setup(directory_name)
    elif (MODE == 2):
        monitor_setup(parent_directory)
    elif (MODE == 3):
        monitor_setup(root_path)
    else:
        print("[Main] Error: Unknown Mode")  

    # Monitoring begins
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
