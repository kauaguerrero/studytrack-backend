import requests
import json

TOKEN = "SEU_TOKEN_DE_ACESSO_TEMPORÁRIO_AQUI"
PHONE_NUMBER_ID = "ID_DO_SEU_NUMERO_DE_TELEFONE_AQUI"
TO_WHATSAPP_NUMBER = "NUMERO_DO_DESTINATARIO_COM_CODIGO_DO_PAIS" # Ex: 5511999998888

url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "messaging_product": "whatsapp",
    "to": TO_WHATSAPP_NUMBER,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "pt_BR"
        }
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.json())