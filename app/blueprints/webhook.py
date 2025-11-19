from flask import Blueprint, request, jsonify, current_app
from app.services.task_service import process_incoming_message

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/whatsapp", methods=["GET"])
def verify_whatsapp_webhook():
    """
    GET /api/webhook/whatsapp
    Verificação de assinatura do Webhook (exigido pela Meta)
    """
    verify_token = current_app.config["META_VERIFY_TOKEN"]

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # Valida o token
    if mode == "subscribe" and token == verify_token:
        print("Webhook (GET) verificado com sucesso!")
        return challenge, 200
    else:
        print("Falha na verificação (GET) do Webhook.")
        return "Falha na verificação", 403


@webhook_bp.route("/whatsapp", methods=["POST"])
def receive_whatsapp_message():
    """
    Recebe eventos da Evolution API.
    """
    data = request.get_json()

    # Processa a mensagem em background (nao bloqueia a resposta)
    # Para MVP, chamamos direto.
    print(f"[Webhook] Recebido payload...")

    # Chama o serviço que criamos
    process_incoming_message(data)

    return jsonify(status="ok"), 200
