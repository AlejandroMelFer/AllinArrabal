import os
import time
import json
import threading
from google import genai
from PIL import Image
from dotenv import load_dotenv
import unicodedata
import zipfile

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


class FileProcessor:
    def __init__(self, strings):
        self.api_key = "AIzaSyB-NAPti6oCfgbddVaslNM6Y2E4efaNUVw"
        self.s = strings
        self.client = genai.Client(api_key=self.api_key)

    def get_unique_path(self, path):
        if not os.path.exists(path):
            return path
        
        base, ext = os.path.splitext(path)
        counter = 1
        while os.path.exists(f"{base} ({counter}){ext}"):
            counter += 1
        return f"{base} ({counter}){ext}"

    def start_processing(self, files_list, prefix, params, status_cb, finish_cb):
        thread = threading.Thread(target=self._run, args=(files_list, prefix, params, status_cb, finish_cb))
        thread.daemon = True
        thread.start()

    def _run(self, files_list, prefix, params, status_cb, finish_cb):
        if not files_list:
            finish_cb()
            return

        renamed_files = []

        for index, file_path in enumerate(files_list):
            filename = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)
            status_cb(file_path, "START", False)

            if not params:
                # No parameters, do not rename
                status_cb(file_path, file_path, False)
                continue

            try:
                # Construir el prompt dinámico
                fields_str = ", ".join(params)
                json_keys_str = ", ".join([f'"{p}": "..."' for p in params])
                prompt = self.s["ai_prompt_renombre"].format(fields=fields_str, json_keys=json_keys_str)
                
                extension = os.path.splitext(filename)[1].lower()

                if extension == '.pdf':
                    with open(file_path, 'rb') as f:
                        uploaded_file = self.client.files.upload(file=f, config={'mime_type': 'application/pdf'})
                    response = self.client.models.generate_content(
                        model='gemini-flash-latest',
                        contents=[prompt, uploaded_file]
                    )
                text_response = response.text
                json_str = text_response.replace('```json', '').replace('```', '').strip()
                data = json.loads(json_str)

                # Construir el nombre de archivo con los valores del JSON
                values = []
                for p in params:
                    val = remove_accents(data.get(p, "")).replace(" ", "_")
                    if val:
                        values.append(val)
                
                full_name = "_".join(values)
                # Limpiar posibles dobles guiones bajos
                while "__" in full_name:
                    full_name = full_name.replace("__", "_")
                full_name = full_name.strip("_")

                new_name = f"{prefix}{full_name}{extension}"

                new_path = os.path.join(folder_path, new_name)
                
                # Solo renombramos si el nombre es distinto al original
                if new_path != file_path:
                    # Asegurar nombre único tipo Windows si choca con OTRO archivo
                    new_path = self.get_unique_path(new_path)
                    os.rename(file_path, new_path)
                    status_cb(file_path, new_path, False)
                else:
                    # Si el nombre es el mismo, lo marcamos como éxito sin mover nada
                    status_cb(file_path, file_path, False)
                
                renamed_files.append(new_path)

                if index < len(files_list) - 1:
                    time.sleep(4) 

            except Exception as e:
                status_cb(file_path, str(e), True)

        if renamed_files:
            try:
                base_dir = os.path.dirname(renamed_files[0])
                zip_name = f"{prefix}Renombrados.zip" if prefix else "Archivos_Renombrados.zip"
                zip_path = os.path.join(base_dir, zip_name)
                
                if os.path.exists(zip_path):
                    try:
                        os.remove(zip_path)
                    except Exception:
                        pass
                
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for f in renamed_files:
                        zf.write(f, os.path.basename(f))
            except Exception as e:
                print(f"Error al crear el zip: {e}")

        finish_cb()

    def start_extracting(self, files_list, params, status_cb, finish_cb):
        thread = threading.Thread(target=self._run_extraction, args=(files_list, params, status_cb, finish_cb))
        thread.daemon = True
        thread.start()

    def _run_extraction(self, files_list, params, status_cb, finish_cb):
        if not files_list:
            finish_cb([])
            return

        extracted_rows = []
        total = len(files_list)
        success_count = 0

        for index, file_path in enumerate(files_list):
            filename = os.path.basename(file_path)
            status_cb(file_path, "START", False)

            if not params:
                status_cb(file_path, self.s["status_no_columns"], True)
                continue

            try:
                # 1. Construir el prompt dinámico
                fields_str = ", ".join(params)
                json_keys_str = ", ".join([f'"{p}": "..."' for p in params])
                prompt = self.s["ai_prompt_extraccion"].format(fields=fields_str, json_keys=json_keys_str)

                # 2. Subir PDF a Gemini
                with open(file_path, 'rb') as f:
                    uploaded_file = self.client.files.upload(file=f, config={'mime_type': 'application/pdf'})

                # 3. Llamar al modelo de IA
                response = self.client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=[prompt, uploaded_file]
                )

                text_response = response.text
                json_str = text_response.replace('```json', '').replace('```', '').strip()
                data = json.loads(json_str)

                # Guardar fila de datos en memoria (manteniendo acentos originales)
                row_data = {}
                for p in params:
                    row_data[p] = str(data.get(p, "")).strip()

                if "_options" in data:
                    row_data["_options"] = data["_options"]

                extracted_rows.append(row_data)
                success_count += 1
                status_cb(file_path, self.s["status_extracted"].format(current=success_count, total=total), False)

                # 4. Evitar límites de cuota (sleep de 4s entre llamadas)
                if index < len(files_list) - 1:
                    time.sleep(4)

            except Exception as e:
                status_cb(file_path, str(e), True)

        finish_cb(extracted_rows)
