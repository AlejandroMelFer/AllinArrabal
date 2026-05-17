import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
from tkinterdnd2 import TkinterDnD, DND_FILES

class TkinterDnDCTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window: return
        x = self.widget.winfo_pointerx() + 15
        y = self.widget.winfo_pointery() + 15
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True)
        self.tooltip_window.configure(bg="#444444", bd=0, highlightthickness=0)
        self.tooltip_window.bind("<Leave>", self.hide_tooltip)
        
        label = ctk.CTkLabel(self.tooltip_window, text=self.text, justify="left", 
                             fg_color="#444444", text_color="white",
                             corner_radius=6, padx=10, pady=5, font=ctk.CTkFont(size=12))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass
            self.tooltip_window = None

class UnifiedFileDropZone(ctk.CTkFrame):
    def __init__(self, master, strings, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.s = strings
        
        self.selected_files = []
        self._file_statuses = {}
        self.is_processing = False
        self.dot_count = 0

        # Area Unificada de Archivos (Drop Zone + Lista)
        self.file_list_frame = ctk.CTkTextbox(self, height=250, wrap="none", cursor="hand2")
        self.file_list_frame.pack(fill="both", expand=True)
        
        # Registrar DND en el propio cuadro de texto
        self.file_list_frame.drop_target_register(DND_FILES)
        self.file_list_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # Configurar colores
        self.file_list_frame.tag_config("success", foreground="#2ecc71")
        self.file_list_frame.tag_config("error", foreground="#ff6b6b")
        self.file_list_frame.tag_config("processing", foreground="#f39c12")
        self.file_list_frame.tag_config("center", justify="center")
        self.file_list_frame.configure(state="disabled")

        # Clic para explorar (solo si está vacío)
        self.file_list_frame.bind("<Button-1>", lambda e: self.browse_files())

        self.refresh_file_list()

    def clear_list(self):
        if self.is_processing:
            return
        self.selected_files = []
        self._file_statuses = {}
        self.refresh_file_list()
        if hasattr(self.master, "on_drop_zone_change"):
            self.master.on_drop_zone_change()

    def on_drop(self, event):
        if self.is_processing:
            return

        # Si ya se procesó anteriormente (existen estados guardados), limpiamos todo primero
        if self._file_statuses:
            self.selected_files = []
            self._file_statuses = {}
            if hasattr(self.master, "on_drop_zone_change"):
                self.master.on_drop_zone_change()

        files = self.tk.splitlist(event.data)
        for f in files:
            if os.path.isfile(f):
                self.add_file(f)

    def browse_files(self):
        if self.is_processing:
            return

        # Si ya se procesó anteriormente, permitimos explorar y limpiar si se eligen archivos nuevos
        if self._file_statuses:
            files = filedialog.askopenfilenames(filetypes=[(self.s["file_dialog_filter"], "*.pdf")])
            if files:
                self.selected_files = []
                self._file_statuses = {}
                if hasattr(self.master, "on_drop_zone_change"):
                    self.master.on_drop_zone_change()
                for f in files:
                    self.add_file(f)
            return

        if self.selected_files:
            return
            
        files = filedialog.askopenfilenames(filetypes=[(self.s["file_dialog_filter"], "*.pdf")])
        for f in files:
            self.add_file(f)

    def add_file(self, file_path):
        if not file_path.lower().endswith(".pdf"):
            return
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
            self.refresh_file_list(self._file_statuses)
            if hasattr(self.master, "on_drop_zone_change"):
                self.master.on_drop_zone_change()

    def refresh_file_list(self, statuses=None):
        if statuses is None:
            statuses = {}

        self.file_list_frame.configure(state="normal")
        self.file_list_frame.delete("1.0", "end")
        
        if not self.selected_files:
            self.file_list_frame.insert("end", "\n\n\n" + self.s["drop_zone_default"], "center")
            self.file_list_frame.configure(cursor="hand2")
        else:
            self.file_list_frame.configure(cursor="arrow")
            for f_path in self.selected_files:
                filename = os.path.basename(f_path)
                if f_path in statuses:
                    status, is_error = statuses[f_path]
                    if status == "START":
                        dots = "." * self.dot_count
                        self.file_list_frame.insert("end", f"{filename} {dots}\n", "processing")
                    elif is_error:
                        self.file_list_frame.insert("end", f"{filename} - Error: {status}\n", "error")
                    else:
                        if status.lower().endswith(".pdf"):
                            display_text = os.path.basename(status)
                        else:
                            display_text = status
                        self.file_list_frame.insert("end", f"{display_text}\n", "success")
                else:
                    self.file_list_frame.insert("end", f"{filename}\n")
        
        self.file_list_frame.configure(state="disabled")
        self.file_list_frame.see("end")

    def update_file_status(self, file_path, status, is_error=False):
        self._file_statuses[file_path] = (status, is_error)
        self.refresh_file_list(self._file_statuses)

    def animate_dots(self):
        if not self.is_processing:
            return
        self.dot_count = (self.dot_count % 3) + 1
        self.refresh_file_list(self._file_statuses)
        self.after(500, self.animate_dots)
