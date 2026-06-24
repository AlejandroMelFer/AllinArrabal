import json
import os
import sys
import queue
import threading
import webview
from logic.processor import FileProcessor
from logic.logic_extract_excel import ExcelLogic
from logic.logic_extract_word import WordLogic

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = _BASE_DIR
    return os.path.join(base_path, relative_path)


import requests

class AllinArrabalAPI:
    def __init__(self):
        path = resource_path("strings.json")
        with open(path, "r", encoding="utf-8") as f:
            self._strings = json.load(f)
        self._processor = FileProcessor(strings=self._strings)
        self._progress_queue = queue.Queue()
        self._window = None
        self._extracted_rows = []
        self._user_email = None
        self._auth_type = None

    def set_window(self, window):
        self._window = window

    # ── Strings ──────────────────────────────────────────────────
    def get_strings(self):
        return self._strings

    def get_extracted_rows(self):
        return self._extracted_rows

    # ── File pickers (native dialogs) ───────────────────────────
    def pick_pdf_files(self):
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=("PDF files (*.pdf)",)
        )
        return list(result) if result else []

    def pick_docx_template(self):
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("Word documents (*.docx)",)
        )
        return result[0] if result else ""

    def get_placeholders_from_template(self, template_path):
        placeholders, placeholders_map, regex_placeholders = WordLogic.extract_placeholders(template_path)
        return {
            "placeholders": placeholders,
            "placeholders_map": placeholders_map,
            "regex_placeholders": list(regex_placeholders)
        }

    # ── Helpers for callbacks ──────────────────────────────────
    def _status_cb(self, file_path, status, is_error):
        self._progress_queue.put({
            "type": "status",
            "file": file_path,
            "status": status,
            "is_error": is_error
        })

    def _finish_cb_rename(self):
        self._progress_queue.put({"type": "rename_done"})

    def _finish_cb_extract(self, rows):
        self._extracted_rows.extend(rows)
        self._progress_queue.put({"type": "extract_done", "row_count": len(self._extracted_rows)})

    # ── Rename ───────────────────────────────────────────────────
    def start_rename(self, files, prefix, params, completed_map=None):
        self._progress_queue.queue.clear()
        self._processor.start_processing(
            files, prefix, params,
            self._status_cb,
            self._finish_cb_rename,
            completed_map,
            email=self._user_email
        )
        return {"status": "started"}

    # ── Extract Excel ────────────────────────────────────────────
    def start_extract_excel(self, files, columns, completed_rows=None):
        self._progress_queue.queue.clear()
        self._extracted_rows = list(completed_rows) if completed_rows else []
        
        completed_files = {row["_file_path"] for row in self._extracted_rows if "_file_path" in row}
        remaining_files = [f for f in files if f not in completed_files]
        
        self._processor.start_extracting(
            remaining_files, columns,
            self._status_cb,
            self._finish_cb_extract,
            email=self._user_email
        )
        return {"status": "started"}

    # ── Extract Word ─────────────────────────────────────────────
    def start_extract_word(self, files, columns, completed_rows=None):
        self._progress_queue.queue.clear()
        self._extracted_rows = list(completed_rows) if completed_rows else []
        
        completed_files = {row["_file_path"] for row in self._extracted_rows if "_file_path" in row}
        remaining_files = [f for f in files if f not in completed_files]
        
        self._processor.start_extracting(
            remaining_files, columns,
            self._status_cb,
            self._finish_cb_extract,
            email=self._user_email
        )
        return {"status": "started"}

    # ── Save results ────────────────────────────────────────────
    def save_excel(self, columns, rows):
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename="datos_extraidos.xlsx",
            file_types=("Excel files (*.xlsx)",)
        )
        if not result:
            return {"success": False, "error": "Cancelado por el usuario"}
        save_path = result[0] if isinstance(result, (list, tuple)) else result
        if not save_path.endswith(".xlsx"):
            save_path += ".xlsx"
        try:
            ExcelLogic.generate_excel(columns, rows, save_path)
            return {"success": True, "path": save_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_word_zip(self, rows, template_path, placeholders_map, regex_placeholders):
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename="documentos.zip",
            file_types=("ZIP files (*.zip)",)
        )
        if not result:
            return {"success": False, "error": "Cancelado por el usuario"}
        save_path = result[0] if isinstance(result, (list, tuple)) else result
        if not save_path.endswith(".zip"):
            save_path += ".zip"
        try:
            count = WordLogic.generate_word_documents(
                rows, template_path, placeholders_map,
                set(regex_placeholders) if regex_placeholders else set(),
                save_path
            )
            return {"success": True, "count": count, "path": save_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Progress polling ──────────────────────────────────────────
    def get_progress_events(self):
        events = []
        try:
            while True:
                events.append(self._progress_queue.get_nowait())
        except queue.Empty:
            pass
        return events

    # ── Window controls (frameless) ─────────────────────────────
    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def toggle_maximize_window(self):
        """Toggle between maximized and normal window state."""
        try:
            import ctypes
            hwnd = int(self._window.native.Handle.ToInt64())
            SW_SHOWMAXIMIZED = 3
            SW_RESTORE = 9
            placement = (ctypes.c_uint * 11)()
            ctypes.windll.user32.GetWindowPlacement(hwnd, placement)
            if int(placement[1]) == SW_SHOWMAXIMIZED:
                ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
            else:
                ctypes.windll.user32.ShowWindow(hwnd, SW_SHOWMAXIMIZED)
        except Exception as e:
            print(f"Error toggling maximize: {e}")

    def is_maximized(self):
        """Returns True if the window is currently maximized."""
        try:
            import ctypes
            hwnd = int(self._window.native.Handle.ToInt64())
            SW_SHOWMAXIMIZED = 3
            placement = (ctypes.c_uint * 11)()
            ctypes.windll.user32.GetWindowPlacement(hwnd, placement)
            return int(placement[1]) == SW_SHOWMAXIMIZED
        except Exception:
            return False

    def close_window(self):
        if self._window:
            self._window.destroy()

    # ── Authentication ──────────────────────────────────────────
    def authenticate_user(self, email):
        try:
            url = f"{self._processor.server_url}/ai/auth"
            r = requests.post(url, json={"email": email}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("success"):
                    self.set_user_session(email, "company")
                    return {"success": True, "role": "company", "email": email}
                else:
                    return {"success": False, "error": data.get("message", "El correo no es corporativo")}
            else:
                return {"success": False, "error": f"Error del servidor ({r.status_code})"}
        except Exception as e:
            return {"success": False, "error": f"No se pudo conectar al servidor: {e}"}

    def set_guest_session(self):
        self.set_user_session("guest", "guest")
        return {"success": True, "role": "guest", "email": "guest"}

    def set_user_session(self, email, auth_type):
        self._user_email = email
        self._auth_type = auth_type
        return {"status": "ok"}
