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

    def on_deleted(self, event):
        logging.info(f"Deleted: {event.src_path}")

    def on_moved(self, event):
        logging.info(f"Moved: {event.src_path} to {event.dest_path}")
        dest_name = os.path.basename(event.dest_path)
        src_name = os.path.basename(event.src_path)
        print(dest_name)
        try:
            self.patterns.append(dest_name)
            self.patterns.remove(src_name)
        except:
            print("Error on rename/move operation!")
            self.patterns.append(dest_name)
        # Print patterns for testing purposes
        print(self.patterns)
    
    def check_cui(self):
        for file in os.listdir(directory_name):
            # sha1_hash = self.sha1_sum(file)
            # print(f"File: {file} SHA1: {sha1_hash}")
            cui_status = self.compare_hash(file)
            # print(f"CUI? {cui_status}")
            if (cui_status):
                # print(f"{file} is CUI, adding to patterns list")
                self.patterns.append(file)
        print(self.patterns)

    def sha1_sum(self, filename):
        # read in 64kb chunks, so we don't eat all the memory in the system
        BUFFER_SIZE = 65536
        sha1 = hashlib.sha1()
        with open(filename, "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sha1.update(data)
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
    patterns = []

# Set up the CUI monitor
if __name__ == "__main__":
    # Get directory path and path of CUI
    directory_name = os.path.dirname(__file__)

    # Monitoring setup
    event_handler = cuiHandler()
    observer = Observer()
    observer.schedule(event_handler, directory_name, recursive = True)

    cuiHandler().check_cui()

    # Monitoring begins
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()