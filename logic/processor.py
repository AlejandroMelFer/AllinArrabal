import os
import time
import json
import threading
import requests
import mimetypes
from dotenv import load_dotenv
import unicodedata
import zipfile

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


class FileProcessor:
    def __init__(self, strings):
        load_dotenv()
        self.server_url = os.getenv("SERVER_URL", "http://13.36.124.182")
        self.s = strings

    def get_unique_path(self, path):
        if not os.path.exists(path):
            return path
        
        base, ext = os.path.splitext(path)
        counter = 1
        while os.path.exists(f"{base} ({counter}){ext}"):
            counter += 1
        return f"{base} ({counter}){ext}"

    def start_processing(self, files_list, prefix, params, status_cb, finish_cb, completed_map=None, email=None):
        thread = threading.Thread(target=self._run, args=(files_list, prefix, params, status_cb, finish_cb, completed_map, email))
        thread.daemon = True
        thread.start()

    def _run(self, files_list, prefix, params, status_cb, finish_cb, completed_map=None, email=None):
        if not files_list:
            finish_cb()
            return

        renamed_files = []

        for index, file_path in enumerate(files_list):
            filename = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)

            if completed_map and file_path in completed_map:
                new_path = completed_map[file_path]
                status_cb(file_path, new_path, False)
                renamed_files.append(new_path)
                continue

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

                # Petición al servidor AWS para procesar el renombrado con la IA
                url = f"{self.server_url}/ai/rename"
                headers = {}
                if email:
                    headers["X-User-Email"] = email
                mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f, mime_type)}
                    data_payload = {'params_json': json.dumps(params)}
                    r = requests.post(url, files=files, data=data_payload, headers=headers)
                
                if r.status_code != 200:
                    raise Exception(f"Error del servidor API ({r.status_code}): {r.text}")
                
                data = r.json()

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

    def start_extracting(self, files_list, params, status_cb, finish_cb, email=None):
        thread = threading.Thread(target=self._run_extraction, args=(files_list, params, status_cb, finish_cb, email))
        thread.daemon = True
        thread.start()

    def _run_extraction(self, files_list, params, status_cb, finish_cb, email=None):
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

                # Petición al servidor AWS para extraer los datos con la IA
                url = f"{self.server_url}/ai/extract"
                headers = {}
                if email:
                    headers["X-User-Email"] = email
                mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f, mime_type)}
                    data_payload = {'params_json': json.dumps(params)}
                    r = requests.post(url, files=files, data=data_payload, headers=headers)

                if r.status_code != 200:
                    raise Exception(f"Error del servidor API ({r.status_code}): {r.text}")
                
                data = r.json()

                # Guardar fila de datos en memoria (manteniendo acentos originales)
                row_data = {}
                row_data["_file_path"] = file_path
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
