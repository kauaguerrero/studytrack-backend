from datetime import date
from app.utils.supabase_client import get_supabase
from app.services.whatsapp_service import send_message


def toggle_task_status(task_id: str):
    """
    Inverte o status da tarefa (pending <-> completed).
    Usado pelo Checkbox da Web.
    """
    supabase = get_supabase()

    try:
        # 1. Busca a tarefa atual
        response = (
            supabase.table("plan_tasks").select("status").eq("id", task_id).execute()
        )
        if not response.data:
            return None, "Tarefa não encontrada"

        current_status = response.data[0]["status"]
        new_status = "completed" if current_status == "pending" else "pending"

        # 2. Atualiza
        update_response = (
            supabase.table("plan_tasks")
            .update({"status": new_status})
            .eq("id", task_id)
            .execute()
        )

        return update_response.data[0], None
    except Exception as e:
        return None, str(e)


def process_incoming_message(payload: dict):
    """
    Processa mensagens recebidas via Webhook (Evolution API).
    Se for 'FEITO', marca a tarefa de hoje como concluída.
    """
    try:
        data = payload.get("data", {})
        key = data.get("key", {})
        message = data.get("message", {})

        # 1. Extrair Telefone e Texto
        remote_jid = key.get("remoteJid", "")  # Ex: 551699...@s.whatsapp.net
        if not remote_jid:
            return "Sem ID"

        # Pega o texto
        text = message.get("conversation") or message.get(
            "extendedTextMessage", {}
        ).get("text")
        if not text:
            return "Sem texto"

        # 2. Verifica o comando
        if text.strip().upper() == "FEITO":
            return _handle_feito_command(remote_jid)

        return "Comando ignorado"

    except Exception as e:
        print(f"Erro processando mensagem: {e}")
        return str(e)


def _handle_feito_command(remote_jid: str):
    """Lógica específica do comando FEITO"""
    supabase = get_supabase()
    today = date.today().isoformat()
    phone_clean = remote_jid.replace("@s.whatsapp.net", "")

    # 1. Achar o usuário pelo telefone
    user_res = (
        supabase.table("profiles")
        .select("id, full_name")
        .or_(f"whatsapp_phone.eq.{phone_clean},whatsapp_phone.eq.{remote_jid}")
        .execute()
    )

    if not user_res.data:
        print(f"Usuário não encontrado para o telefone {phone_clean}")
        return "User not found"

    user = user_res.data[0]
    user_id = user["id"]
    first_name = user["full_name"].split(" ")[0]

    # 2. Achar a tarefa de HOJE pendente
    task_res = (
        supabase.table("plan_tasks")
        .select("id, task_description")
        .eq("user_id", user_id)
        .eq("scheduled_date", today)
        .eq("status", "pending")
        .execute()
    )

    if not task_res.data:
        # Talvez já tenha feito?
        send_message(
            remote_jid,
            f"Oi {first_name}! Não achei tarefas pendentes para hoje. Ou você já acabou, ou é dia de folga! 🎉",
        )
        return "Sem tarefas pendentes"

    # 3. Marcar como concluída (todas as pendentes de hoje)
    for task in task_res.data:
        supabase.table("plan_tasks").update({"status": "completed"}).eq(
            "id", task["id"]
        ).execute()

    # 4. Celebrar!
    send_message(
        remote_jid,
        f"Boa, {first_name}! 🚀\nTarefa '{task_res.data[0]['task_description']}' concluída.\nStreak mantido! 🔥",
    )

    return "Tarefa concluída via WhatsApp"
