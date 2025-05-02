import time
import logging
import os
import hashlib
import platform
from watchdog.observers import Observer
from watchdog.events import *

'''
Other things worth adding or improving:
1. HASH Database not hardcoded. (half/done)
Currently, the hashes present to determine whether something is CUI is in the program itself.
There is no way to change these currently, (if the file changes, CUI hashes will not change)
'''

DEBUG_MODE = False

# Set up the logging file and format
logging.basicConfig(
    filename = "file_changes.log",
    level = logging.INFO,
    format = "%(asctime)s - %(message)s"
)

class cuiHandler(PatternMatchingEventHandler):
    def on_modified(self, event):
        logging.info(f'Modified: {event.src_path}')

    def on_created(self, event):
        self.check_cui(event.src_path)
        logging.info(f"Created: {event.src_path}")

    def on_deleted(self, event):
        logging.info(f"Deleted: {event.src_path}")

    def on_moved(self, event):
        logging.info(f"Moved: {event.src_path} to {event.dest_path}")
        # check to see if destination is in ignore and remove if so (solves undo problem)
        if event.dest_path in self.ignore_patterns:
            self.ignore_patterns.remove(event.dest_path)
        try:
            self.patterns.append(event.dest_path)
            # self.patterns.remove(event.src_path)
        except:
            print("Source not in patterns")
            self.patterns.append(event.dest_path)
            # self.ignore_patterns.append(src_name)
        # Print patterns for testing purposes
        print(f"Patterns: {self.patterns}")
        print(f"Ignored: {self.ignore_patterns}")
    
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
        if DEBUG_MODE:
            print(f"Patterns: {self.patterns}")
            print(f"Ignored: {self.ignore_patterns}")

    def check_cui(self, filename):
        cui_status = self.compare_hash(filename)
        if DEBUG_MODE:
            print(f"[check_cui] File: {filename}, CUI: {cui_status}")
        if (cui_status == False):
            # in the setup_cui function run, it will check everything
            # we only want to put things in ignore_patterns that are in patterns
            # can try to be generalized by splicing the list
            # or be specific with what we have right now
            if (((".txt" in filename) or (".cui" in filename)) and ((".vscode" in filename) == False)): # specific case
                if DEBUG_MODE:
                    print(f"[check_cui] File: {filename} is FoI")
                self.ignore_patterns.append(filename)
        else: # file is cui
            if ((".txt" not in filename) and (".cui" not in filename) and (".enc" not in filename)):
                self.patterns.append(filename)
    
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
        cui_hashes = self.hashes
        if sha3_hash in cui_hashes:
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
    patterns = ["*.txt", "*.cui", "*.enc"]
    ignore_patterns = ["file_changes.log","hashdatabase.txt"]
    # ignore_directories = True
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

# Set up the CUI monitor
if __name__ == "__main__":
    # Get directory path and path of CUI
    # 0 = Home Directory, 
    # 1 = Parent Directory, 
    # 2 = Parent Parent Directory (testing)
    MODE = 0 
    SKIP_SETUP = False

    home_path = os.path.expanduser("~")
    directory_name = os.path.dirname(__file__)
    parent_directory = os.path.dirname(directory_name)

    # Monitoring setup
    event_handler = cuiHandler()
    observer = Observer()
    if (MODE == 0):
        monitor_setup(home_path)
    elif (MODE == 1):
        monitor_setup(directory_name)
    elif (MODE == 2):
        monitor_setup(parent_directory)
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
