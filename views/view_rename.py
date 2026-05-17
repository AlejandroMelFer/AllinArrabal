import customtkinter as ctk
import os
from views.components import UnifiedFileDropZone, Tooltip

class RenameView(ctk.CTkFrame):
    def __init__(self, master, strings, start_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.s = strings
        self.start_callback = start_callback

        self.label_title = ctk.CTkLabel(self, text="Renombrado de documentos", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=(20, 10))

        # --- Parameters Section ---
        self.frame_params_container = ctk.CTkFrame(self)
        self.frame_params_container.pack(padx=20, pady=5, fill="x")
        
        self.params_list_frame = ctk.CTkFrame(self.frame_params_container, fg_color="transparent")
        self.params_list_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.frame_params_actions = ctk.CTkFrame(self.frame_params_container, fg_color="transparent")
        self.frame_params_actions.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_add_param = ctk.CTkButton(self.frame_params_actions, text=self.s["btn_add_param"], 
                                           command=self.add_rename_param_ui, width=150)
        self.btn_add_param.pack(side="left")

        self.help_icon = ctk.CTkLabel(self.frame_params_actions, text="?", 
                                      text_color="#3498db", font=ctk.CTkFont(size=18, weight="bold"),
                                      cursor="question_arrow")
        self.help_icon.pack(side="left", padx=10)
        Tooltip(self.help_icon, self.s["help_tooltip"])

        self.param_entries = []
        self.add_rename_param_ui("Apellidos")
        self.add_rename_param_ui("Nombre")

        # --- Prefix Section ---
        self.frame_prefix = ctk.CTkFrame(self)
        self.frame_prefix.pack(padx=20, pady=5, fill="x")
        self.frame_prefix.grid_columnconfigure(1, weight=1)
        self.label_prefix = ctk.CTkLabel(self.frame_prefix, text=self.s["prefix_label"])
        self.label_prefix.grid(row=0, column=0, padx=10, pady=10)
        self.entry_prefix = ctk.CTkEntry(self.frame_prefix, placeholder_text=self.s["placeholder_prefix"])
        self.entry_prefix.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Drop Zone ---
        self.rename_drop_zone = UnifiedFileDropZone(self, strings=self.s)
        self.rename_drop_zone.pack(padx=20, pady=10, fill="both", expand=True)

        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.pack(padx=20, pady=10, fill="x")

        self.btn_run = ctk.CTkButton(self.frame_actions, text=self.s["btn_start"], command=self.on_start_click, 
                                     fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(weight="bold"))
        self.btn_run.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_clear = ctk.CTkButton(self.frame_actions, text=self.s["btn_clear_list"], command=self.clear_list,
                                       fg_color="#555555", hover_color="#444444", font=ctk.CTkFont(weight="bold"))
        self.btn_clear.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def add_rename_param_ui(self, default_text=""):
        from tkinter import messagebox
        if len(self.param_entries) >= 5:
            messagebox.showwarning(self.s["warning_title"], self.s.get("error_max_params", "Maximum parameters reached."))
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
        self.rename_drop_zone.clear_list()

    def on_start_click(self):
        prefix = self.entry_prefix.get()
        params = [e.get().strip() for e in self.param_entries if e.get().strip()]

        if not self.rename_drop_zone.selected_files:
            return

        self.rename_drop_zone.is_processing = True
        self.rename_drop_zone.dot_count = 0
        self.rename_drop_zone.animate_dots()
        self.btn_run.configure(state="disabled", text=self.s["btn_processing"])
        
        self.start_callback(self.rename_drop_zone.selected_files, prefix, params)

    def unlock_ui(self):
        self.rename_drop_zone.is_processing = False
        self.rename_drop_zone.refresh_file_list(self.rename_drop_zone._file_statuses)
        self.btn_run.configure(state="normal", text=self.s["btn_start"])
