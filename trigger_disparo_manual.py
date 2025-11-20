import requests
import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("CRON_SECRET")
URL = "http://127.0.0.1:5000/api/cron/trigger-daily"

print(f"Testando disparo para: {URL}")

try:
    response = requests.post(URL, headers={"Authorization": f"Bearer {SECRET}"})

    print(f"Status Code: {response.status_code}")
    print(f"Resposta: {response.text}")

    if response.status_code == 200:
        print("✅ SUCESSO! Cron disparado.")
    elif response.status_code == 401:
        print("❌ ERRO 401: Não autorizado. Verifique a senha no .env")
    else:
        print("❌ ERRO: Algo deu errado.")

except Exception as e:
    print(f"Erro de conexão: {e}")
    print("O servidor Flask está rodando?")
