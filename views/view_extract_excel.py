import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from logic.logic_extract_excel import ExcelLogic
from views.components import UnifiedFileDropZone, Tooltip

class ExtractExcelView(ctk.CTkFrame):
    def __init__(self, master, strings, start_extract_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.s = strings
        self.start_extract_callback = start_extract_callback
        self._extracted_rows = []

        self.label_extract_title = ctk.CTkLabel(self, text="Extraer a hoja de calculo", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_extract_title.pack(pady=(20, 10))

        # --- Parameters Section (Extraction) ---
        self.frame_extract_params_container = ctk.CTkFrame(self)
        self.frame_extract_params_container.pack(padx=20, pady=5, fill="x")
        
        self.extract_params_list_frame = ctk.CTkScrollableFrame(self.frame_extract_params_container, fg_color="transparent", height=200)
        self.extract_params_list_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.frame_extract_params_actions = ctk.CTkFrame(self.frame_extract_params_container, fg_color="transparent")
        self.frame_extract_params_actions.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_extract_add_param = ctk.CTkButton(self.frame_extract_params_actions, text="Anadir columna / dato", 
                                                   command=self.add_extract_param_ui, width=180)
        self.btn_extract_add_param.pack(side="left")

        self.extract_help_icon = ctk.CTkLabel(self.frame_extract_params_actions, text="?", 
                                              text_color="#2ecc71", font=ctk.CTkFont(size=18, weight="bold"),
                                              cursor="question_arrow")
        self.extract_help_icon.pack(side="left", padx=10)
        Tooltip(self.extract_help_icon, "Anade los nombres de las columnas o datos que quieres extraer del PDF al documento de Excel (ej: Nombre, Apellido, DNI, Email).")

        self.extract_param_entries = []
        self.add_extract_param_ui("Nombre")
        self.add_extract_param_ui("Apellido 1")
        self.add_extract_param_ui("Apellido 2")
        self.add_extract_param_ui("DNI")
        self.add_extract_param_ui("Email")
        self.add_extract_param_ui("Fecha de nacimiento")
        self.add_extract_param_ui("Dirección")
        self.add_extract_param_ui("Teléfono")
        self.add_extract_param_ui("Género")

        # --- Drop Zone ---
        self.extract_drop_zone = UnifiedFileDropZone(self, strings=self.s)
        self.extract_drop_zone.pack(padx=20, pady=10, fill="both", expand=True)

        self.frame_extract_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_extract_actions.pack(padx=20, pady=(5, 10), fill="x")

        self.btn_extract_run = ctk.CTkButton(
            self.frame_extract_actions, text=self.s["btn_extract_start"],
            command=self.on_extract_click,
            fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold")
        )
        self.btn_extract_run.pack(fill="x", pady=(0, 6))

        self.frame_extract_output_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_extract_output_btns.pack(padx=20, pady=(0, 10), fill="x")

        self.btn_create_excel = ctk.CTkButton(
            self.frame_extract_output_btns, text=self.s["btn_create_excel"],
            command=self.on_create_excel,
            fg_color="#1a7a4a", hover_color="#156038", font=ctk.CTkFont(weight="bold")
        )
        self.btn_create_excel.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_extract_clear = ctk.CTkButton(
            self.frame_extract_output_btns, text=self.s["btn_clear_extract"],
            command=self.clear_extract_list,
            fg_color="#555555", hover_color="#444444", font=ctk.CTkFont(weight="bold")
        )
        self.btn_extract_clear.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.update_output_buttons_state()

    def add_extract_param_ui(self, default_text=""):
        frame = ctk.CTkFrame(self.extract_params_list_frame, fg_color="transparent")
        frame.pack(fill="x", pady=2)

        entry = ctk.CTkEntry(frame)
        if default_text:
            entry.insert(0, default_text)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_del = ctk.CTkButton(frame, text="X", width=30, fg_color="#e74c3c", hover_color="#c0392b",
                                command=lambda f=frame, e=entry: self.remove_param(f, e))
        btn_del.pack(side="right")
        self.extract_param_entries.append(entry)
        self.update_extract_scrollbar()

    def remove_param(self, frame, entry):
        frame.destroy()
        if entry in self.extract_param_entries:
            self.extract_param_entries.remove(entry)
        self.update_extract_scrollbar()

    def update_extract_scrollbar(self):
        if hasattr(self, "extract_params_list_frame") and hasattr(self.extract_params_list_frame, "_scrollbar"):
            if len(self.extract_param_entries) > 6:
                self.extract_params_list_frame._scrollbar.grid()
            else:
                self.extract_params_list_frame._scrollbar.grid_remove()

    def clear_extract_list(self):
        self.extract_drop_zone.clear_list()
        self._extracted_rows = []
        self.update_output_buttons_state()

    def update_output_buttons_state(self):
        if getattr(self, "_extracted_rows", []):
            self.btn_create_excel.configure(state="normal")
        else:
            self.btn_create_excel.configure(state="disabled")

    def on_drop_zone_change(self):
        self._extracted_rows = []
        self.update_output_buttons_state()

    def on_extract_click(self):
        columns = [e.get().strip() for e in self.extract_param_entries if e.get().strip()]

        if not self.extract_drop_zone.selected_files:
            messagebox.showinfo(self.s["info_no_files_title"], self.s["info_no_files_msg"])
            return

        if not columns:
            messagebox.showwarning(self.s["warn_no_cols_title"], self.s["warn_no_cols_msg"])
            return

        self.extract_drop_zone.is_processing = True
        self.extract_drop_zone.dot_count = 0
        self.extract_drop_zone.animate_dots()
        self.btn_extract_run.configure(state="disabled", text=self.s["btn_processing"])
        self.btn_create_excel.configure(state="disabled")

        self.start_extract_callback(self.extract_drop_zone.selected_files, columns)

    def unlock_ui(self, extracted_rows):
        self.extract_drop_zone.is_processing = False
        self.extract_drop_zone.refresh_file_list(self.extract_drop_zone._file_statuses)
        self.btn_extract_run.configure(state="normal", text=self.s["btn_extract_start"])
        self._extracted_rows = extracted_rows
        self.update_output_buttons_state()

    def on_create_excel(self):
        columns = [e.get().strip() for e in self.extract_param_entries if e.get().strip()]
        extracted_rows = getattr(self, "_extracted_rows", [])

        if not columns:
            messagebox.showwarning(self.s["warn_no_cols_title"], self.s["warn_no_cols_msg"])
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[(self.s["excel_filter_name"], "*.xlsx")],
            title=self.s["excel_save_title"]
        )
        if not save_path:
            return

        try:
            ExcelLogic.generate_excel(columns, extracted_rows, save_path)
            messagebox.showinfo(
                self.s["excel_success_title"],
                self.s["excel_success_msg"].format(path=save_path, cols=len(columns), rows=len(extracted_rows))
            )

        except Exception as e:
            messagebox.showerror(self.s["excel_error_title"], str(e))
