import json
import os
import ctypes
from views.gui import AllinArrabalGUI
from logic.processor import FileProcessor
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

try:
    myappid = 'com.allinarrabal.docprocessor.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass


def load_strings():
    path = resource_path("strings.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    strings = load_strings()
    processor = None
    
    def handle_start(path, prefix, params):
        processor.start_processing(path, prefix, params, app.update_rename_status, app.unlock_ui)

    def handle_extract(path, params):
        processor.start_extracting(path, params, app.update_extract_status, app.unlock_extract_ui)

    app = AllinArrabalGUI(
        start_callback=handle_start, 
        start_extract_callback=handle_extract, 
        strings=strings
    )

    processor = FileProcessor(strings=strings)


    app.mainloop()

if __name__ == "__main__":
    main()
