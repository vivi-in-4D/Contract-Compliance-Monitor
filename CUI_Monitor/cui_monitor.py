import time
import logging
import os
import hashlib
from watchdog.observers import Observer
from watchdog.events import *

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
            # print("Source not in patterns")
            self.patterns.append(event.dest_path)
            # self.ignore_patterns.append(src_name)
        # Print patterns for testing purposes
        # print(f"Patterns: {self.patterns}")
        # print(f"Ignored: {self.ignore_patterns}")
    
    # Into Non-watchdog functions 
    def setup_cui(self, path):
        print(f"Path: {path}")
        for file in os.listdir(path):
            self.check_cui(os.path.abspath(file))
        # print(f"Patterns: {self.patterns}")
        # print(f"Ignored: {self.ignore_patterns}")

    def check_cui(self, filename):
        cui_status = self.compare_hash(filename)
        # print(f"File: {filename}, CUI: {cui_status}")
        if (cui_status == False):
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
            # print("Error: [sha1sum], couldn't open file")
            return False
        # print(f"File: {filename}, Hash: {sha1.hexdigest()}")
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
    ignore_directories=True

# Set up the CUI monitor
if __name__ == "__main__":
    # Get directory path and path of CUI
    MODE = 1 # 0 = home mode, 1 = directory_name mode

    directory_name = os.path.dirname(__file__)
    home_path = os.path.expanduser("~")

    # Monitoring setup
    event_handler = cuiHandler()
    observer = Observer()
    if (MODE == 0):
        observer.schedule(event_handler, home_path, recursive = True)
        cuiHandler().setup_cui(home_path)
    elif (MODE == 1):
        observer.schedule(event_handler, directory_name, recursive = True)
        cuiHandler().setup_cui(directory_name)
    else:
        print("Error: Unknown Mode")  

    # Monitoring begins
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
