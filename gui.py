import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import ctypes
import sys
from tkinterdnd2 import TkinterDnD, DND_FILES

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


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
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True)
        
        label = ctk.CTkLabel(self.tooltip_window, text=self.text, justify="left", 
                             fg_color="#444444", text_color="white",
                             corner_radius=6, padx=10, pady=5, font=ctk.CTkFont(size=12))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class AllinArrabalGUI(TkinterDnDCTk):
    def __init__(self, start_callback, strings):
        super().__init__()

        self.start_callback = start_callback
        self.s = strings

        # Configuracion de la ventana
        self.title(self.s["app_title"])
        self.geometry("950x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.set_icon()

        self.label_title = ctk.CTkLabel(self, text="AllinArrabal", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=(20, 10))

        self.selected_files = []


        # --- Parameters Section ---
        self.frame_params_container = ctk.CTkFrame(self)
        self.frame_params_container.pack(padx=20, pady=5, fill="x")
        
        # Lista de parámetros (sin scroll)
        self.params_list_frame = ctk.CTkFrame(self.frame_params_container, fg_color="transparent")
        self.params_list_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Contenedor para botón e icono (abajo)
        self.frame_params_actions = ctk.CTkFrame(self.frame_params_container, fg_color="transparent")
        self.frame_params_actions.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_add_param = ctk.CTkButton(self.frame_params_actions, text=self.s["btn_add_param"], 
                                           command=self.add_param_ui, width=150)
        self.btn_add_param.pack(side="left")

        self.help_icon = ctk.CTkLabel(self.frame_params_actions, text=self.s["help_label"], 
                                      text_color="#3498db", font=ctk.CTkFont(size=18, weight="bold"),
                                      cursor="question_arrow")
        self.help_icon.pack(side="left", padx=10)
        Tooltip(self.help_icon, self.s["help_tooltip"])




        self.param_entries = []
        # Valores por defecto
        self.add_param_ui("Apellidos")
        self.add_param_ui("Nombre")

        # --- Prefix Section ---
        self.frame_prefix = ctk.CTkFrame(self)
        self.frame_prefix.pack(padx=20, pady=5, fill="x")
        self.frame_prefix.grid_columnconfigure(1, weight=1)
        self.label_prefix = ctk.CTkLabel(self.frame_prefix, text=self.s["prefix_label"])
        self.label_prefix.grid(row=0, column=0, padx=10, pady=10)
        self.entry_prefix = ctk.CTkEntry(self.frame_prefix, placeholder_text=self.s["placeholder_prefix"])
        self.entry_prefix.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Drop Zone ---
        # --- Area Unificada de Archivos (Drop Zone + Lista) ---
        self.file_list_frame = ctk.CTkTextbox(self, height=250, wrap="none", cursor="hand2")
        self.file_list_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
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

        self.is_processing = False
        self.dot_count = 0

        self.refresh_file_list() # Mostrar mensaje inicial


        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.pack(padx=20, pady=10, fill="x")

        self.btn_run = ctk.CTkButton(self.frame_actions, text=self.s["btn_start"], command=self.on_start_click, 
                                     fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(weight="bold"))
        self.btn_run.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_clear = ctk.CTkButton(self.frame_actions, text=self.s["btn_clear_list"], command=self.clear_list,
                                       fg_color="#555555", hover_color="#444444", font=ctk.CTkFont(weight="bold"))
        self.btn_clear.pack(side="right", fill="x", expand=True, padx=(5, 0))


    def set_icon(self):
        icon_path = resource_path(os.path.join("assets", "ODF.ico"))
        if os.path.exists(icon_path):

            try:
                from PIL import Image, ImageTk
                # Cargar el icono con PIL para mayor compatibilidad
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                
                # Aplicar el icono de múltiples formas para asegurar la barra de tareas
                self.wm_iconphoto(True, photo)
                self.iconphoto(True, photo)
                self.iconbitmap(os.path.abspath(icon_path))
                
                # Guardar referencia para evitar el Garbage Collector
                self._icon_ref = photo
            except Exception as e:
                print(f"No se pudo cargar el icono: {e}")


    def add_param_ui(self, default_text=""):
        if len(self.param_entries) >= 5:
            messagebox.showwarning(self.s["warning_title"], self.s["error_max_params"])
            return

        
        frame = ctk.CTkFrame(self.params_list_frame, fg_color="transparent")
        frame.pack(fill="x", pady=2)

        
        entry = ctk.CTkEntry(frame)
        if default_text:
            entry.insert(0, default_text)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_del = ctk.CTkButton(frame, text="X", width=30, fg_color="#e74c3c", hover_color="#c0392b",
                                command=lambda f=frame, e=entry: self.remove_param(f, e))
        btn_del.pack(side="right")
        self.param_entries.append(entry)

    def remove_param(self, frame, entry):
        frame.destroy()
        if entry in self.param_entries:
            self.param_entries.remove(entry)

    def clear_list(self):
        if self.is_processing:
            return
        self.selected_files = []
        if hasattr(self, '_file_statuses'):
            self._file_statuses = {}
        self.refresh_file_list()



    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            if os.path.isfile(f):
                self.add_file(f)

    def browse_files(self):
        # Desactivar el click si ya hay archivos
        if self.selected_files:
            return
            
        files = filedialog.askopenfilenames(filetypes=[(self.s["file_dialog_filter"], "*.png;*.jpg;*.jpeg;*.pdf")])
        for f in files:
            self.add_file(f)

    def add_file(self, file_path):
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
            self.refresh_file_list(getattr(self, '_file_statuses', {}))

    def refresh_file_list(self, statuses=None):
        """Redibuja la lista completa o muestra el mensaje de inicio"""
        if statuses is None:
            statuses = {}

        self.file_list_frame.configure(state="normal")
        self.file_list_frame.delete("1.0", "end")
        
        if not self.selected_files:
            # Si no hay archivos, mostrar el mensaje de "Arrastra aquí"
            # Añadimos unos saltos de línea para centrarlo un poco verticalmente
            self.file_list_frame.insert("end", "\n\n\n" + self.s["drop_zone_default"], "center")
            self.file_list_frame.configure(cursor="hand2")
        else:
            self.file_list_frame.configure(cursor="arrow")
            for f_path in self.selected_files:
                filename = os.path.basename(f_path)
                if f_path in statuses:
                    status, is_error = statuses[f_path]
                    if status == "START":
                        dots = "." * getattr(self, 'dot_count', 1)
                        self.file_list_frame.insert("end", f"{filename} {dots}\n", "processing")
                    elif is_error:
                        self.file_list_frame.insert("end", f"{filename} - Error: {status}\n", "error")
                    else:
                        new_filename = os.path.basename(status)
                        self.file_list_frame.insert("end", f"{new_filename}\n", "success")
                else:
                    self.file_list_frame.insert("end", f"{filename}\n")
        
        self.file_list_frame.configure(state="disabled")
        self.file_list_frame.see("end")


    def update_file_status(self, file_path, status, is_error=False):
        # Guardamos los estados actuales para redibujar
        if not hasattr(self, '_file_statuses'):
            self._file_statuses = {}
        
        self._file_statuses[file_path] = (status, is_error)
        self.refresh_file_list(self._file_statuses)





    def animate_dots(self):
        if not self.is_processing:
            return
        self.dot_count = (self.dot_count % 3) + 1
        if hasattr(self, '_file_statuses'):
            self.refresh_file_list(self._file_statuses)
        self.after(500, self.animate_dots)

    def on_start_click(self):
        prefix = self.entry_prefix.get()
        # Obtener parametros no vacios
        params = [e.get().strip() for e in self.param_entries if e.get().strip()]

        if not self.selected_files:
            return

        self.is_processing = True
        self.dot_count = 0
        self.animate_dots()
        self.btn_run.configure(state="disabled", text=self.s["btn_processing"])
        
        self.start_callback(self.selected_files, prefix, params)


    def unlock_ui(self):
        self.is_processing = False
        self.refresh_file_list(getattr(self, '_file_statuses', {}))
        self.btn_run.configure(state="normal", text=self.s["btn_start"])
