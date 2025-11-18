import requests
import os
from flask import current_app


def send_message(phone_number: str, text: str):
    """
    Envia mensagem de texto via Evolution API v2.
    Endpoint: /message/sendText/{instance}
    """
    try:
        base_url = current_app.config["EVOLUTION_BASE_URL"]
        api_key = current_app.config["EVOLUTION_API_KEY"]
        instance = current_app.config["EVOLUTION_INSTANCE_NAME"]

        # Limpeza básica do número
        clean_phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")

        # 1. Garante o DDI 55 (Brasil) se não tiver
        if len(clean_phone) <= 11:
            clean_phone = f"55{clean_phone}"

        # 2. Adiciona o sufixo do WhatsApp se não tiver
        if "@s.whatsapp.net" not in clean_phone:
            full_phone = f"{clean_phone}@s.whatsapp.net"
        else:
            full_phone = clean_phone

        url = f"{base_url}/message/sendText/{instance}"

        headers = {
            "apikey": api_key,
            "Content-Type": "application/json",
        }

        # --- CORREÇÃO DO PAYLOAD (V2) ---
        # O erro disse: 'textMessage is not of a type(s) object'
        # Então vamos enviar um objeto JSON dentro de textMessage.
        payload = {
            "number": full_phone,
            "options": {"delay": 1200, "presence": "composing", "linkPreview": False},
            "textMessage": {"text": text},
        }

        print(f"[Evolution] Enviando para {full_phone} na instância {instance}...")

        response = requests.post(url, json=payload, headers=headers)

        # Debug detalhado em caso de erro
        if response.status_code != 200 and response.status_code != 201:
            print(f"[Evolution] Erro API ({response.status_code}): {response.text}")
            return False

        print(f"[Evolution] Sucesso: {response.json()}")
        return True

    except Exception as e:
        print(f"[Evolution] Erro Fatal ao enviar: {e}")
        return False


# --- Scripts da Fase 0 (Mantidos Iguais) ---


def send_welcome_message(phone_number: str, name: str):
    """Script 1: Boas-Vindas"""

    text = (
        f"Olá {name}, aqui é o Mentor AI! 👋\n\n"
        "Recebi seu número! Seu acesso está confirmado. 🚀\n\n"
        "Estou usando meu novo sistema (Evolution) para falar com você mais rápido.\n"
        "Amanhã começamos!"
    )

    send_message(phone_number, text)
