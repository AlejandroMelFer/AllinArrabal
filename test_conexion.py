import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: No se encontro la API Key en el archivo .env")
    exit()

client = genai.Client(api_key=api_key)

print("Intentando conectar con Gemini...")

try:
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents="Dime: 'Conexion exitosa con el nuevo motor de AllinArrabal'"
    )


    
    print("\nTODO LISTO")
    print(f"Respuesta de la IA: {response.text}")
    print("\nEl nuevo motor de Google GenAI esta funcionando correctamente.")

except Exception as e:
    print(f"\nERROR al conectar: {e}")
    print("\nConsejo: Verifica que tu API Key sea correcta y tengas internet.")
