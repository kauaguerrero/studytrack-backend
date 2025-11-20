from flask import Blueprint, jsonify, request
import os
from app.services.scheduler_service import process_daily_tasks

scheduler_bp = Blueprint("scheduler", __name__)


@scheduler_bp.route("/trigger-daily", methods=["POST", "GET"])
def trigger_daily_cron():
    """
    Rota para disparar manualmente o envio de tarefas.
    Protegida por uma CRON_SECRET nas variáveis de ambiente.
    """

    expected_secret = os.environ.get("CRON_SECRET")

    if not expected_secret:
        print("ERRO: CRON_SECRET não configurado no servidor.")
        return jsonify(error="Server misconfiguration"), 500

    auth_header = request.headers.get("Authorization")

    if auth_header and "Bearer " in auth_header:
        received_token = auth_header.split(" ")[1]
    else:
        received_token = auth_header

    if received_token != expected_secret:
        return jsonify(error="Unauthorized"), 401

    try:
        result = process_daily_tasks()
        return jsonify(status="completed", details=result), 200
    except Exception as e:
        print(f"Erro na execução do Cron: {e}")
        return jsonify(error=str(e)), 500
