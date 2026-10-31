import json
import mimetypes
import os
import tempfile
import time

import requests
from dotenv import load_dotenv
from fastapi import (
    Body,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
)
from google import genai
from google.genai import types
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

def get_file_mime_type(filename: str, content_type: str) -> tuple:
    ext = os.path.splitext(filename or "")[1].lower()
    if not ext:
        ext = ".pdf"
    mime_type = content_type
    if not mime_type or mime_type in ("application/octet-stream", "content/unknown"):
        mime_type, _ = mimetypes.guess_type(filename or "")
    if not mime_type:
        if ext in (".jpg", ".jpeg"):
            mime_type = "image/jpeg"
        elif ext == ".png":
            mime_type = "image/png"
        elif ext == ".webp":
            mime_type = "image/webp"
        else:
            mime_type = "application/pdf"
    return ext, mime_type


app = FastAPI(title="AllinArrabal AI API", description="API para procesar documentos con Gemini")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Cargar strings.json
STRINGS_PATH = "strings.json"
with open(STRINGS_PATH, "r", encoding="utf-8") as f:
    strings = json.load(f)

# Configuración API Arrabal IT
ARRABAL_LOGIN_URL = os.getenv("ARRABAL_LOGIN_URL", "https://app.arrabal-api.org/arrabal-it-back/auth/login")
ARRABAL_USERS_URL = os.getenv("ARRABAL_USERS_URL", "https://app.arrabal-api.org/arrabal-it-back/user/allUsers")
ARRABAL_API_USER = os.getenv("ARRABAL_API_USER")
ARRABAL_API_PASS = os.getenv("ARRABAL_API_PASS")
if not ARRABAL_API_PASS:
    raise RuntimeError("Falta la variable de entorno de la contraseña de la API")
_arrabal_emails_cache = set()
_arrabal_cache_time = 0
_CACHE_TTL = 600  # 10 minutos

def get_arrabal_active_emails() -> set:
    global _arrabal_emails_cache, _arrabal_cache_time
    now = time.time()
    if _arrabal_emails_cache and (now - _arrabal_cache_time < _CACHE_TTL):
        return _arrabal_emails_cache

    try:
        login_res = requests.post(
            ARRABAL_LOGIN_URL,
            json={"username": ARRABAL_API_USER, "password": ARRABAL_API_PASS},
            timeout=10
        )
        if login_res.status_code != 200:
            print(f"Error login Arrabal API: {login_res.status_code} - {login_res.text}")
            return _arrabal_emails_cache
        
        token = login_res.json().get("token")
        if not token:
            print("No se recibió token de Arrabal API")
            return _arrabal_emails_cache

        users_res = requests.get(
            ARRABAL_USERS_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if users_res.status_code != 200:
            print(f"Error obteniendo usuarios de Arrabal API: {users_res.status_code}")
            return _arrabal_emails_cache

        users_list = users_res.json()
        emails = set()
        if isinstance(users_list, list):
            for u in users_list:
                if isinstance(u, dict):
                    email = u.get("email") or u.get("username")
                    if email and isinstance(email, str):
                        clean_email = email.strip().lower()
                        if clean_email and "@" in clean_email:
                            emails.add(clean_email)
        
        _arrabal_emails_cache = emails
        _arrabal_cache_time = now
        return _arrabal_emails_cache
    except Exception as e:
        print(f"Excepción al conectar con Arrabal API: {e}")
        return _arrabal_emails_cache

def is_valid_arrabal_user(email: str) -> bool:
    if not email:
        return False
    clean_email = email.strip().lower()
    active_emails = get_arrabal_active_emails()
    if clean_email in active_emails:
        return True
    # Si la lista en caché está vacía (por fallo temporal de API), fallback a dominio
    return bool(not active_emails and clean_email.endswith("@arrabalempleo.org"))

def get_api_key_and_model(x_user_email: str = None) -> tuple:
    if not x_user_email:
        raise HTTPException(status_code=401, detail="Falta cabecera de autenticación X-User-Email")

    email = x_user_email.strip().lower()
    model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

    if is_valid_arrabal_user(email):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY de pago no configurada en el servidor")
    else:
        api_key = os.getenv("FREE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="FREE_API_KEY no configurada en el servidor")

    return api_key, model

@app.get("/")
def root():
    return {"status": "ok", "message": "AllinArrabal AI Server Running"}

@app.post("/ai/auth")
async def ai_auth(payload: dict = Body(...)):
    email = payload.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="El correo es obligatorio")
    
    if is_valid_arrabal_user(email):
        return {
            "success": True,
            "status": "success",
            "role": "company",
            "email": email,
            "message": "Autenticado correctamente como usuario registrado en Arrabal"
        }
    else:
        return {
            "success": False,
            "status": "error",
            "role": "guest",
            "message": "El correo no pertenece a un usuario activo de Arrabal. Inicie sesión como invitado."
        }

@app.post("/ai/rename")
@limiter.limit("5/minute")
async def ai_rename(
    request: Request,
    file: UploadFile = File(...),
    params_json: str = Form("[]"),
    x_user_email: str = Header(default=None)
):
    api_key, model = get_api_key_and_model(x_user_email)

    try:
        params = json.loads(params_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="params_json debe ser un JSON válido")

    client = genai.Client(api_key=api_key)

    try:
        file_bytes = await file.read()
        _, mime_type = get_file_mime_type(file.filename, file.content_type)
        file_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)

        # Construir el prompt dinámico
        fields_str = ", ".join(params)
        json_keys_str = ", ".join([f'"{p}": "..."' for p in params])
        prompt = strings["ai_prompt_renombre"].format(fields=fields_str, json_keys=json_keys_str)

        response = client.models.generate_content(
            model=model,
            contents=[prompt, file_part]
        )
        
        text_response = response.text
        json_str = text_response.replace('```json', '').replace('```', '').strip()
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/extract")
@limiter.limit("5/minute")
async def ai_extract(
    request: Request,
    file: UploadFile = File(...),
    params_json: str = Form("[]"),
    x_user_email: str = Header(default=None)
):
    api_key, model = get_api_key_and_model(x_user_email)

    try:
        params = json.loads(params_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="params_json debe ser un JSON válido")

    client = genai.Client(api_key=api_key)

    try:
        file_bytes = await file.read()
        _, mime_type = get_file_mime_type(file.filename, file.content_type)
        file_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)

        # Construir el prompt dinámico
        fields_str = ", ".join(params)
        json_keys_str = ", ".join([f'"{p}": "..."' for p in params])
        prompt = strings["ai_prompt_extraccion"].format(fields=fields_str, json_keys=json_keys_str)

        response = client.models.generate_content(
            model=model,
            contents=[prompt, file_part]
        )
        
        text_response = response.text
        json_str = text_response.replace('```json', '').replace('```', '').strip()
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
