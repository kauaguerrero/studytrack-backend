from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.supabase_client import get_supabase

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")


@dashboard_bp.route("/dashboard")
def home():
    """GET /dashboard"""
    supabase = get_supabase()
    user_data = None

    access_token = request.cookies.get("sb-access-token")
    if not access_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and "Bearer " in auth_header:
            access_token = auth_header.split(" ")[1]

    if access_token:
        try:
            # Valida o usuário com o Supabase
            user_response = supabase.auth.get_user(access_token)
            if user_response and user_response.user:
                user = user_response.user
                # Busca dados extras na tabela profiles
                profile_response = (
                    supabase.table("profiles")
                    .select("full_name, whatsapp_phone")
                    .eq("id", user.id)
                    .execute()
                )

                profile = profile_response.data[0] if profile_response.data else {}

                user_data = {
                    "name": profile.get("full_name", "Estudante"),
                    "email": user.email,
                    "id": user.id,
                }
        except Exception as e:
            print(f"Erro ao validar token no dashboard flask: {e}")

    # Se não conseguiu autenticar, usa dados de fallback ou redireciona
    if not user_data:
        # Opção A: Redirecionar para login (comentado para não travar seu teste)
        # return redirect("http://localhost:3000/auth/login")
        user_data = {"name": "Visitante (Não Logado)", "email": "faça@login.com"}

    tasks_data = []
    if user_data.get("id"):
        try:
            response = (
                supabase.table("plan_tasks")
                .select("*")
                .eq("user_id", user_data["id"])
                .limit(5)
                .execute()
            )
            for t in response.data:
                tasks_data.append(
                    {
                        "desc": t.get("task_description"),
                        "done": t.get("status") == "completed",
                    }
                )
        except Exception as e:
            print(f"Erro ao buscar tarefas: {e}")

    if not tasks_data:
        tasks_data = [
            {"desc": "Exemplo: Estudar Python", "done": True},
            {"desc": "Faça login para ver suas tarefas reais", "done": False},
        ]

    return render_template("dashboard.html", user=user_data, tasks=tasks_data)
