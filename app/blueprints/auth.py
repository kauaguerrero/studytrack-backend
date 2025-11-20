import token
from flask import Blueprint, request, jsonify
import supabase
from app.services.auth_service import complete_onboarding
from app.utils.supabase_client import get_supabase

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/onboarding/complete", methods=["POST"])
def handle_onboarding():
    """POST /api/auth/onboarding/complete"""

    # 1. Verifica o Header Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or "Bearer " not in auth_header:
        return jsonify({"error": "Token de autenticação ausente"}), 401

    token = auth_header.split(" ")[1]

    supabase = get_supabase()
    try:
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            return jsonify({"error": "Token inválido ou expirado"}), 401
        user_id = user_response.user.id

    except Exception as e:
        print(f"Erro ao validar token: {e}")
        return jsonify({"error": "Falha na autenticação"}), 401

    # 2. Processamento dos dados
    data = request.get_json()
    phone = data.get("whatsapp_phone")

    if not phone:
        return jsonify(error="whatsapp_phone é obrigatório"), 400

    if not phone:
        return jsonify(error="whatsapp_phone é obrigatório"), 400

    # Delega a lógica para o service layer
    result, error = complete_onboarding(user_id, phone)

    if error:
        return jsonify(error=error), 500

    return jsonify(success=True, data=result), 200
