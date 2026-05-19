import customtkinter as ctk
import os
from views.components import TkinterDnDCTk

from views.view_rename import RenameView
from views.view_extract_excel import ExtractExcelView
from views.view_extract_word import ExtractWordView

def resource_path(relative_path):
    import sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AllinArrabalGUI(TkinterDnDCTk):
    def __init__(self, start_callback, start_extract_callback, strings):
        super().__init__()

        self.start_callback = start_callback
        self.start_extract_callback = start_extract_callback
        self.s = strings

        # Configuracion de la ventana
        self.title(self.s["app_title"])
        self.geometry("950x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.set_icon()

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=80, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        
        # Icono 1: Renombrar
        rename_icon_path = resource_path(os.path.join("assets", "Renombre.jpeg"))
        self.rename_icon = None
        if os.path.exists(rename_icon_path):
            try:
                from PIL import Image
                img = Image.open(rename_icon_path)
                self.rename_icon = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))
            except Exception as e:
                pass

        self.btn_rename_feature = ctk.CTkButton(self.sidebar_frame, text="", image=self.rename_icon, 
                                                width=60, height=60, fg_color="#333333", 
                                                hover_color="#333333",
                                                command=lambda: self.show_view("rename"))
        self.btn_rename_feature.pack(pady=(20, 10), padx=10)

        # Icono 2: Extraer Excel
        extract_excel_icon_path = resource_path(os.path.join("assets", "DocToSheet.jpeg"))
        self.extract_excel_icon = None
        if os.path.exists(extract_excel_icon_path):
            try:
                from PIL import Image
                img = Image.open(extract_excel_icon_path)
                self.extract_excel_icon = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))
            except Exception as e:
                pass

        self.btn_extract_excel_feature = ctk.CTkButton(self.sidebar_frame, text="", image=self.extract_excel_icon, 
                                                 width=60, height=60, fg_color="transparent", 
                                                 hover_color="#333333",
                                                 command=lambda: self.show_view("extract_excel"))
        self.btn_extract_excel_feature.pack(pady=10, padx=10)

        # Icono 3: Extraer Word
        extract_word_icon_path = resource_path(os.path.join("assets", "DocToText.jpeg"))
        self.extract_word_icon = None
        if os.path.exists(extract_word_icon_path):
            try:
                from PIL import Image
                img = Image.open(extract_word_icon_path)
                self.extract_word_icon = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))
            except Exception as e:
                pass

        self.btn_extract_word_feature = ctk.CTkButton(self.sidebar_frame, text="", image=self.extract_word_icon, 
                                                 width=60, height=60, fg_color="transparent", 
                                                 hover_color="#333333",
                                                 command=lambda: self.show_view("extract_word"))
        self.btn_extract_word_feature.pack(pady=10, padx=10)

        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="left", fill="both", expand=True)

        # Initialize Views
        self.rename_view = RenameView(self.main_frame, self.s, self.start_callback)
        self.extract_excel_view = ExtractExcelView(self.main_frame, self.s, self.start_extract_callback)
        self.extract_word_view = ExtractWordView(self.main_frame, self.s, self.start_extract_callback)

        self.current_view = None
        self.show_view("rename")

    def show_view(self, view_name):
        if self.current_view:
            self.current_view.pack_forget()

        self.btn_rename_feature.configure(fg_color="transparent")
        self.btn_extract_excel_feature.configure(fg_color="transparent")
        self.btn_extract_word_feature.configure(fg_color="transparent")

        if view_name == "rename":
            self.rename_view.pack(fill="both", expand=True)
            self.btn_rename_feature.configure(fg_color="#333333")
            self.current_view = self.rename_view
        elif view_name == "extract_excel":
            self.extract_excel_view.pack(fill="both", expand=True)
            self.btn_extract_excel_feature.configure(fg_color="#333333")
            self.current_view = self.extract_excel_view
        elif view_name == "extract_word":
            self.extract_word_view.pack(fill="both", expand=True)
            self.btn_extract_word_feature.configure(fg_color="#333333")
            self.current_view = self.extract_word_view

    def set_icon(self):
        icon_path = resource_path(os.path.join("assets", "ODF.ico"))
        if os.path.exists(icon_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.wm_iconphoto(True, photo)
                self.iconphoto(True, photo)
                self.iconbitmap(os.path.abspath(icon_path))
                self._icon_ref = photo
            except Exception as e:
                pass

    # Passthroughs para main.py
    def update_rename_status(self, file_path, status, is_error=False):
        self.rename_view.rename_drop_zone.update_file_status(file_path, status, is_error)

    def unlock_ui(self):
        self.rename_view.unlock_ui()

    def update_extract_status(self, file_path, status, is_error=False):
        if self.current_view == self.extract_excel_view:
            self.extract_excel_view.extract_drop_zone.update_file_status(file_path, status, is_error)
        elif self.current_view == self.extract_word_view:
            self.extract_word_view.pdf_drop_zone.update_file_status(file_path, status, is_error)

    def unlock_extract_ui(self, extracted_rows):
        if self.current_view == self.extract_excel_view:
            self.extract_excel_view.unlock_ui(extracted_rows)
        elif self.current_view == self.extract_word_view:
            self.extract_word_view.unlock_ui(extracted_rows)
