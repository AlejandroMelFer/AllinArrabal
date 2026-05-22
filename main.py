import webview
import os
import sys
import ctypes
from ctypes import wintypes
from api import AllinArrabalAPI

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_custom_wnd_proc = None
_original_wnd_proc = None

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = _BASE_DIR
    return os.path.join(base_path, relative_path)

try:
    myappid = 'com.allinarrabal.docprocessor.v2'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass


def main():
    api = AllinArrabalAPI()
    window = webview.create_window(
        title="AllinArrabal",
        url=resource_path("frontend/dist/index.html"),
        js_api=api,
        width=1100,
        height=800,
        resizable=True,
        frameless=True,
        easy_drag=False,
        min_size=(800, 600)
    )
    api.set_window(window)

    def setup_resizable(win):
        try:
            hwnd = int(win.native.Handle.ToInt64())

            GWL_STYLE = -16
            WS_THICKFRAME   = 0x00040000
            WS_MAXIMIZEBOX  = 0x00010000
            WS_MINIMIZEBOX  = 0x00020000
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            new_style = current_style | WS_THICKFRAME | WS_MAXIMIZEBOX | WS_MINIMIZEBOX
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            ctypes.windll.user32.SetWindowPos(
                hwnd, None, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
            )

            GWL_WNDPROC = -4
            WNDPROC = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
            
            def wnd_proc(hwnd_val, msg, wparam, lparam):
                WM_NCHITTEST = 0x0084
                if msg == WM_NCHITTEST:
                    rect = wintypes.RECT()
                    ctypes.windll.user32.GetWindowRect(hwnd_val, ctypes.byref(rect))
                    
                    x = ctypes.c_short(lparam & 0xFFFF).value
                    y = ctypes.c_short((lparam >> 16) & 0xFFFF).value
                    
                    border_width = 8
                    
                    is_left = (x >= rect.left) and (x < rect.left + border_width)
                    is_right = (x < rect.right) and (x >= rect.right - border_width)
                    is_top = (y >= rect.top) and (y < rect.top + border_width)
                    is_bottom = (y < rect.bottom) and (y >= rect.bottom - border_width)
                    
                    HTLEFT = 10
                    HTRIGHT = 11
                    HTTOP = 12
                    HTTOPLEFT = 13
                    HTTOPRIGHT = 14
                    HTBOTTOM = 15
                    HTBOTTOMLEFT = 16
                    HTBOTTOMRIGHT = 17
                    
                    if is_top and is_left: return HTTOPLEFT
                    if is_top and is_right: return HTTOPRIGHT
                    if is_bottom and is_left: return HTBOTTOMLEFT
                    if is_bottom and is_right: return HTBOTTOMRIGHT
                    if is_left: return HTLEFT
                    if is_right: return HTRIGHT
                    if is_top: return HTTOP
                    if is_bottom: return HTBOTTOM
                
                return ctypes.windll.user32.CallWindowProcW(_original_wnd_proc, hwnd_val, msg, wparam, lparam)
            
            global _custom_wnd_proc, _original_wnd_proc
            _custom_wnd_proc = WNDPROC(wnd_proc)
            
            _original_wnd_proc = ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_WNDPROC, _custom_wnd_proc)
            if not _original_wnd_proc:
                _original_wnd_proc = ctypes.windll.user32.SetWindowLongW(hwnd, GWL_WNDPROC, _custom_wnd_proc)
        except Exception as e:
            print(f"Error setting up native resizable hooks: {e}")

    def bind_drag_drop(win):
        import json
        from webview.dom import DOMEventHandler

        def on_drop(e):
            try:
                files = e.get('dataTransfer', {}).get('files', [])
                paths = []
                for f in files:
                    p = f.get('pywebviewFullPath')
                    if p:
                        paths.append(p)
                if paths:
                    escaped_paths = json.dumps(paths)
                    win.evaluate_js(f"window.dispatchEvent(new CustomEvent('pywebviewfilesdropped', {{ detail: {escaped_paths} }}));")
            except Exception as ex:
                print(f"Error in drag-drop: {ex}")

        try:
            win.dom.document.events.drop += DOMEventHandler(on_drop, prevent_default=True, stop_propagation=True)
            win.dom.document.events.dragover += DOMEventHandler(lambda e: None, prevent_default=True, stop_propagation=True)
        except Exception as ex:
            print(f"Failed to bind drag-drop: {ex}")

    def on_loaded(*args):
        bind_drag_drop(window)
        setup_resizable(window)

    window.events.loaded += on_loaded
    webview.start(debug=False)

if __name__ == "__main__":
    main()
