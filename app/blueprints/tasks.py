from flask import Blueprint, request, jsonify
from app.utils.supabase_client import get_supabase

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/toggle", methods=["POST"])
def toggle_task():
    """
    POST /api/tasks/toggle
    Recebe { "task_id": "..." } e inverte o status no Supabase.
    """
    supabase = get_supabase()

    try:
        data = request.get_json()
        task_id = data.get("task_id")

        if not task_id:
            return jsonify({"error": "Task ID required"}), 400

        # 1. Busca o status atual
        response = (
            supabase.table("plan_tasks").select("status").eq("id", task_id).execute()
        )

        if not response.data:
            return jsonify({"error": "Task not found"}), 404

        current_status = response.data[0]["status"]
        # Lógica simples de alternância
        new_status = "completed" if current_status != "completed" else "pending"

        # 2. Atualiza para o novo status
        supabase.table("plan_tasks").update({"status": new_status}).eq(
            "id", task_id
        ).execute()

        return jsonify({"message": "Success", "new_status": new_status}), 200

    except Exception as e:
        print(f"ERRO TASK TOGGLE: {str(e)}")
        return jsonify({"error": str(e)}), 500
