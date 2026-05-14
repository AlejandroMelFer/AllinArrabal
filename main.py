import json
import os
import ctypes
from gui import AllinArrabalGUI
from processor import FileProcessor
import sys

def resource_path(relative_path):
    """ Obtiene la ruta absoluta de los recursos, compatible con PyInstaller """
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
        processor.start_processing(path, prefix, params)

    app = AllinArrabalGUI(start_callback=handle_start, strings=strings)

    processor = FileProcessor(
        status_callback=app.update_file_status, 
        finish_callback=app.unlock_ui,
        strings=strings
    )


    app.mainloop()

if __name__ == "__main__":
    main()
