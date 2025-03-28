import time
import logging
import os
import hashlib
from watchdog.observers import Observer
from watchdog.events import *

'''
Other things worth adding or improving:
1. DEBUG mode
Currently, the number of print statements for debugging purposes is quite high, 
so it could be beneficial to add a MODE to toggle them on and off.
this is instead of manually going through and toggling each one.

2. SHA3 Hashes
Currently, we are working with SHA1 hashes.
SHA1 hashes are not industry standard but SHA3 is.

3. HASH Database not hardcoded.
Currently, the hashes present to determine whether something is CUI is in the program itself.
There is no way to change these currently, (if the file changes, CUI hashes will not change)

4. Still need to test Linux
The fix to the directory issue might only work in windows.
The fix if needed would be simple. 
just a function to determine operating system similiar to the hide file function I originally made

5. Test without debug 
(988 seconds with)
could be less without.
If it takes a long time even without print statements, consider making/finding more optimizations
'''

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
        logging.info(f"Created: {event.src_path}")
        src_name = os.path.basename(event.src_path)
        self.check_cui(event.src_path)

    def on_deleted(self, event):
        logging.info(f"Deleted: {event.src_path}")

    def on_moved(self, event):
        logging.info(f"Moved: {event.src_path} to {event.dest_path}")
        dest_name = os.path.basename(event.dest_path)
        src_name = os.path.basename(event.src_path)
        # print(dest_name)
        try:
            self.patterns.append(event.dest_path)
            self.patterns.remove(event.src_path)
        except:
            print("Source not in patterns")
            self.patterns.append(event.dest_path)
            # self.ignore_patterns.append(src_name)
        # Print patterns for testing purposes
        print(f"Patterns: {self.patterns}")
        print(f"Ignored: {self.ignore_patterns}")
    
    # Into Non-watchdog functions 
    def setup_cui(self, dir_path):
        print(f"[setup_cui] Path: {dir_path}")
        # some folders are not accessible by the program (Application Data)
        # as a result, use try/except whenever we use "os.listdir(dir_path)"
        try:
            print(f"[setup_cui] Items in path: {os.listdir(dir_path)}")
            for file in os.listdir(dir_path):
                # fix pathing issue
                file_path = dir_path + "\\" + file # may only work in windows
                print(f"[setup_cui] File: {os.path.abspath(file_path)}")
                # check if folder -> if folder, check inside
                if (os.path.isdir(file_path)):
                    # if folder, check inside
                    print(f"[setup_cui] {file} is directory")
                    print(f"[setup_cui] {file_path} is directory path")
                    self.setup_cui(file_path) # recursion to cover folders in folders
                else:
                    self.check_cui(os.path.abspath(file_path))
        except:
            print("[setup_cui] This folder is not accessible.")
        print(f"Patterns: {self.patterns}")
        print(f"Ignored: {self.ignore_patterns}")

    def check_cui(self, filename):
        cui_status = self.compare_hash(filename)
        print(f"[check_cui] File: {filename}, CUI: {cui_status}")
        if (cui_status == False):
            # in the setup_cui function run, it will check everything
            # we only want to put things in ignore_patterns that are in patterns
            # can try to be generalized by splicing the list
            # or be specific with what we have right now
            if (((".txt" in filename) or (".cui" in filename)) and ((".vscode" in filename) == False)): # specific case
                print(f"[check_cui] File: {filename} is FoI")
                self.ignore_patterns.append(filename)

    def sha1_sum(self, filename):
        # read in 64kb chunks, so we don't eat all the memory in the system
        BUFFER_SIZE = 65536
        sha1 = hashlib.sha1()
        try:
            with open(os.path.abspath(filename), "rb") as f:
                while True:
                    data = f.read(BUFFER_SIZE)
                    if not data:
                        break
                    sha1.update(data)
        except:
            print("[sha1sum] Error: couldn't open file")
            return False
        print(f"[sha1sum] File: {filename}, Hash: {sha1.hexdigest()}")
        return sha1.hexdigest()
    
    def compare_hash(self, filename):
        sha1_hash = self.sha1_sum(filename)
        # This is where you put hashes of all CUI
        cui_hashes = [
                "d4a4cd4a80c8abc6718a3ea80db60dc2783ce3f0",
                "9d174eddc47849cc600084eb94727603c8fcfcb5",
                "da39a3ee5e6b4b0d3255bfef95601890afd80709"] 
        if sha1_hash in cui_hashes:
            return True
        else:
            return False

    # Important: Controls filter!
    patterns = ["*.txt", "*.cui"]
    ignore_patterns = ["file_changes.log"]
    # ignore_directories = True

def monitor_setup(dir_path):
    observer.schedule(event_handler, dir_path, recursive = True)
    start_time = time.time()
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
        print("[MAIN] Error: Unknown Mode")  

    # Monitoring begins
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
