import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import os
from logic.logic_extract_word import WordLogic
from tkinterdnd2 import DND_FILES
from views.components import UnifiedFileDropZone

class WordTemplateDropZone(ctk.CTkFrame):
    def __init__(self, master, strings, on_template_loaded=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.s = strings
        self.on_template_loaded = on_template_loaded
        
        self.template_path = None
        self.placeholders = []
        self.placeholders_map = {}      # Mapeo de celdas vacías (Estrategia B)
        self.regex_placeholders = set() # Placeholders {{}} (Estrategia A)

        # Area de tarjeta premium
        self.card_frame = ctk.CTkFrame(self, height=200, corner_radius=10, border_width=2, border_color="#555555")
        self.card_frame.pack(fill="both", expand=True)
        
        # Registrar DND
        self.card_frame.drop_target_register(DND_FILES)
        self.card_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        self.label_icon = ctk.CTkLabel(self.card_frame, text="📄", font=ctk.CTkFont(size=44))
        self.label_icon.pack(pady=(20, 5))
        
        self.label_text = ctk.CTkLabel(self.card_frame, text=self.s["word_drop_zone_template"], justify="center", font=ctk.CTkFont(size=12))
        self.label_text.pack(pady=10)
        
        # Bind de clics
        self.card_frame.bind("<Button-1>", lambda e: self.browse_template())
        self.label_icon.bind("<Button-1>", lambda e: self.browse_template())
        self.label_text.bind("<Button-1>", lambda e: self.browse_template())

    def clear(self):
        self.template_path = None
        self.placeholders = []
        self.placeholders_map = {}
        self.regex_placeholders = set()
        self.card_frame.configure(border_color="#555555")
        self.label_icon.configure(text="📄", text_color="white")
        self.label_text.configure(text=self.s["word_drop_zone_template"], text_color="white")

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            self.load_template(files[0])

    def browse_template(self):
        f = filedialog.askopenfilename(filetypes=[("Plantilla Word", "*.docx")])
        if f:
            self.load_template(f)

    def load_template(self, file_path):
        if not file_path.lower().endswith(".docx"):
            messagebox.showerror("Error de archivo", "Por favor, selecciona un archivo de plantilla Word válido (.docx)")
            return
            
        try:
            self.template_path = file_path
            self.placeholders, self.placeholders_map, self.regex_placeholders = WordLogic.extract_placeholders(file_path)
            
            filename = os.path.basename(file_path)
            self.card_frame.configure(border_color="#2ecc71")
            self.label_icon.configure(text="📝", text_color="#2ecc71")
            self.label_text.configure(
                text=self.s["word_template_loaded"].format(filename=filename),
                text_color="#2ecc71"
            )
            
            if self.on_template_loaded:
                self.on_template_loaded(self.placeholders)
        except Exception as e:
            messagebox.showerror("Error al leer plantilla", f"No se pudo leer la plantilla:\n{str(e)}")




class ExtractWordView(ctk.CTkFrame):
    def __init__(self, master, strings, start_extract_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.s = strings
        self.start_extract_callback = start_extract_callback
        self._extracted_rows = []

        self.label_extract_title = ctk.CTkLabel(
            self, text="Extracción a documento de texto", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_extract_title.pack(pady=(20, 10))

        # --- Grid de 2 Columnas (Plantilla vs PDFs) ---
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(padx=20, pady=10, fill="both", expand=True)
        self.grid_container.grid_columnconfigure(0, weight=4, uniform="col")
        self.grid_container.grid_columnconfigure(1, weight=6, uniform="col")

        # Columna 1: Plantilla
        self.col_left = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.col_left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.label_col_left = ctk.CTkLabel(
            self.col_left, text="1. Selecciona la Plantilla (.docx)", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_col_left.pack(anchor="w", pady=(0, 5))

        self.template_drop_zone = WordTemplateDropZone(
            self.col_left, strings=self.s, on_template_loaded=self.show_detected_placeholders
        )
        self.template_drop_zone.pack(fill="x", expand=False)

        # Contenedor para mostrar los campos detectados
        self.placeholders_container = ctk.CTkScrollableFrame(self.col_left, height=130, label_text=self.s["word_placeholders_title"])
        self.placeholders_container.pack(fill="both", expand=True, pady=(10, 0))
        
        self.label_no_placeholders = ctk.CTkLabel(
            self.placeholders_container, text=self.s["word_placeholders_none"], text_color="#888888", font=ctk.CTkFont(size=12)
        )
        self.label_no_placeholders.pack(pady=10)

        # Columna 2: PDFs
        self.col_right = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.col_right.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        self.label_col_right = ctk.CTkLabel(
            self.col_right, text="2. Selecciona los Documentos (.pdf)", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_col_right.pack(anchor="w", pady=(0, 5))

        self.pdf_drop_zone = UnifiedFileDropZone(self.col_right, strings=self.s)
        self.pdf_drop_zone.pack(fill="both", expand=True)

        # --- Acciones ---
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.pack(padx=20, pady=(5, 10), fill="x")

        self.btn_run = ctk.CTkButton(
            self.frame_actions, text=self.s["btn_extract_start"],
            command=self.on_extract_click,
            fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold")
        )
        self.btn_run.pack(fill="x", pady=(0, 6))

        self.frame_output_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_output_btns.pack(padx=20, pady=(0, 10), fill="x")

        self.btn_create_word = ctk.CTkButton(
            self.frame_output_btns, text=self.s["btn_create_word"],
            command=self.on_create_word,
            fg_color="#1a4a8a", hover_color="#153870", font=ctk.CTkFont(weight="bold")
        )
        self.btn_create_word.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_clear = ctk.CTkButton(
            self.frame_output_btns, text=self.s["btn_clear_extract"],
            command=self.clear_all,
            fg_color="#555555", hover_color="#444444", font=ctk.CTkFont(weight="bold")
        )
        self.btn_clear.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.update_output_buttons_state()

    def on_drop_zone_change(self):
        self._extracted_rows = []
        self.update_output_buttons_state()

    def show_detected_placeholders(self, placeholders):
        # Limpiar contenedor
        for widget in self.placeholders_container.winfo_children():
            widget.destroy()
            
        if not placeholders:
            self.label_no_placeholders = ctk.CTkLabel(
                self.placeholders_container, text=self.s["word_placeholders_none"], text_color="#888888", font=ctk.CTkFont(size=12)
            )
            self.label_no_placeholders.pack(pady=10)
            return

        # Dibujar badges interactivos con botón de eliminar
        for p in placeholders:
            badge_frame = ctk.CTkFrame(self.placeholders_container, fg_color="#222222", corner_radius=6)
            badge_frame.pack(fill="x", pady=2, padx=5)
            
            badge_lbl = ctk.CTkLabel(
                badge_frame, text=p, text_color="#3498db",
                font=ctk.CTkFont(size=11, family="Consolas"),
                wraplength=170, justify="left"
            )
            badge_lbl.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=3, anchor="w")
            
            btn_del = ctk.CTkButton(
                badge_frame, text="✕", width=18, height=18,
                fg_color="transparent", hover_color="#e74c3c", text_color="#888888",
                font=ctk.CTkFont(size=9, weight="bold"),
                command=lambda val=p, f=badge_frame: self.remove_placeholder(val, f)
            )
            btn_del.pack(side="right", padx=(4, 6), pady=3)
            
        self.update_output_buttons_state()

    def remove_placeholder(self, p, frame):
        # 1. Eliminar de las estructuras de datos en memoria (¡NO se vuelve a parsear el archivo!)
        if p in self.template_drop_zone.placeholders:
            self.template_drop_zone.placeholders.remove(p)
        self.template_drop_zone.placeholders_map.pop(p, None)
        if p in self.template_drop_zone.regex_placeholders:
            self.template_drop_zone.regex_placeholders.remove(p)
            
        # 2. Destruir el elemento visual de forma instantánea sin parpadeos
        frame.destroy()
        
        # 3. Si se han eliminado todos, mostrar el mensaje de "Ninguno"
        if not self.template_drop_zone.placeholders:
            self.label_no_placeholders = ctk.CTkLabel(
                self.placeholders_container, text=self.s["word_placeholders_none"], text_color="#888888", font=ctk.CTkFont(size=12)
            )
            self.label_no_placeholders.pack(pady=10)
            
        self.update_output_buttons_state()

    def clear_all(self):
        self.template_drop_zone.clear()
        self.pdf_drop_zone.clear_list()
        self._extracted_rows = []
        for widget in self.placeholders_container.winfo_children():
            widget.destroy()
        self.label_no_placeholders = ctk.CTkLabel(
            self.placeholders_container, text=self.s["word_placeholders_none"], text_color="#888888", font=ctk.CTkFont(size=12)
        )
        self.label_no_placeholders.pack(pady=10)
        self.update_output_buttons_state()

    def update_output_buttons_state(self):
        if getattr(self, "_extracted_rows", []) and self.template_drop_zone.template_path:
            self.btn_create_word.configure(state="normal")
        else:
            self.btn_create_word.configure(state="disabled")

    def on_extract_click(self):
        if not self.template_drop_zone.template_path:
            messagebox.showwarning("Falta plantilla", "Por favor, arrastra o carga primero la plantilla de Word (.docx).")
            return
            
        if not self.template_drop_zone.placeholders:
            messagebox.showwarning("Plantilla vacía", "No se detectaron campos con formato {{campo}} en la plantilla de Word.")
            return

        if not self.pdf_drop_zone.selected_files:
            messagebox.showinfo(self.s["info_no_files_title"], self.s["info_no_files_msg"])
            return

        self.pdf_drop_zone.is_processing = True
        self.pdf_drop_zone.dot_count = 0
        self.pdf_drop_zone.animate_dots()
        
        self.btn_run.configure(state="disabled", text=self.s["btn_processing"])
        self.btn_create_word.configure(state="disabled")

        # Iniciar callback de extracción en segundo plano usando los placeholders de la plantilla
        self.start_extract_callback(self.pdf_drop_zone.selected_files, self.template_drop_zone.placeholders)

    def unlock_ui(self, extracted_rows):
        self.pdf_drop_zone.is_processing = False
        self.pdf_drop_zone.refresh_file_list(self.pdf_drop_zone._file_statuses)
        self.btn_run.configure(state="normal", text=self.s["btn_extract_start"])
        self._extracted_rows = extracted_rows
        self.update_output_buttons_state()

    def on_create_word(self):
        if not self.template_drop_zone.template_path:
            return
            
        extracted_rows = getattr(self, "_extracted_rows", [])
        if not extracted_rows:
            return

        dest_zip = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("Archivo ZIP", "*.zip")],
            title="Guardar documentos comprimidos"
        )
        if not dest_zip:
            return

        try:
            success_count = WordLogic.generate_word_documents(
                extracted_rows, 
                self.template_drop_zone.template_path, 
                self.template_drop_zone.placeholders_map, 
                self.template_drop_zone.regex_placeholders, 
                dest_zip
            )

            messagebox.showinfo(
                "Archivo ZIP creado",
                f"¡Generados {success_count} documentos de Word rellenados con éxito!\n\nSe han guardado comprimidos en:\n{dest_zip}"
            )

        except Exception as e:
            messagebox.showerror("Error al generar ZIP", f"Ocurrió un error al guardar y comprimir los documentos:\n{str(e)}")
