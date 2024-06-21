import os

from flask import Response
from postgrest import APIResponse
from supabase import create_client, Client
from dataclasses import dataclass
from src.network.utils import check_password


@dataclass
class SupabaseConfig:
    URL: str = 'https://lhmpllwftyjhgbdnhggc.supabase.co'
    KEY: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxobXBsbHdmdHlqaGdiZG5oZ2djIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDY4MDk5MjAsImV4cCI6MjAyMjM4NTkyMH0.6ipiNyj7iZrU3N-23MXsaWieK2DnfcbU2nYeb5V7FSY'
    SECRET: str = ''


supabase: Client = create_client(SupabaseConfig().URL, SupabaseConfig().KEY)


class SupabaseHandler:
    def __init__(self) -> None:
        self._config = SupabaseConfig()
        self._client: Client = create_client(self._config.URL, self._config.KEY)

    @property
    def client(self) -> Client:
        return self._client

    def fetch_all(self, table: str) -> APIResponse:
        response: APIResponse = self._client.table(table).select("*").execute()
        return response

    def fetch(self, table: str, column: str) -> APIResponse:
        response: APIResponse = self._client.table(table).select(column).execute()
        return response

    def insert(self, table: str, data: dict) -> APIResponse:
        return (self._client.table(table).insert(data)).execute()

    def update(self, table: str, data: dict) -> APIResponse:
        return self._client.table(table).update(data).execute()

    def delete(self, table: str, key: str) -> APIResponse:
        return self._client.table(table).delete().execute()


class HoneyPotHandler(SupabaseHandler):
    def __init__(self) -> None:
        super().__init__()

    def fetch_all_logs(self) -> APIResponse:
        return self.fetch_all(table='logs')

    def add_log(self, log: dict) -> APIResponse:
        return self.insert(table='logs', data=log)


class SSHServerCommandHandler(SupabaseHandler):
    def __init__(self) -> None:
        super().__init__()

    def fetch_all_logs(self) -> APIResponse:
        return self.fetch_all(table='ssh_logs')

    def add_log(self, log: dict) -> APIResponse:
        return self.insert(table='ssh_logs', data=log)


class HTTPServerDB(SupabaseHandler):
    def __init__(self) -> None:
        super().__init__()

    def fetch_all_logs(self) -> APIResponse:
        return self.fetch_all(table='http_logs')

    def add_log(self, log: dict) -> APIResponse:
        return self.insert(table='http_logs', data=log)


class AccountDB(SupabaseHandler):
    def __init__(self) -> None:
        super().__init__()

    def verify_user_credentials(self, username: str, password: str) -> Response:
        """
        Vérifie si un utilisateur existe avec le nom d'utilisateur spécifié et si le mot de passe correspond.

        :param username: Le nom d'utilisateur à vérifier.
        :param password: Le mot de passe à vérifier.
        :return: True si l'utilisateur existe et le mot de passe correspond, sinon False.
        """
        # Requête pour trouver l'utilisateur avec le nom d'utilisateur spécifié.
        response = self._client.table("accounts").select("user, password").eq("user", username).execute()
        # Vérifie si la réponse contient des données et si le mot de passe correspond.
        return check_password(response.data[0]['password'].encode(), password)

    def get_hp_name(self, username: str) -> APIResponse:
        response = self._client.table("accounts").select("*").eq("user", username).execute()
        return response

    def get_account(self, name: str) -> APIResponse:
        response = self._client.table("accounts").select("*").eq("name", name).execute()
        return response

    def get_account_by_username(self, username: str) -> APIResponse:
        response = self._client.table("accounts").select("*").eq("user", username).execute()
        return response


class ModuleConfDB(SupabaseHandler):
    def __init__(self) -> None:
        super().__init__()

    def post_conf_json(self, conf: dict):
        return self.insert(table="modules_conf", data=conf)


class StateDB(SupabaseHandler):
    def __init__(self) -> None:
        super().__init__()

    def change_run_state(self, state: bool, honeypot) -> APIResponse:
        return self._client.table("state").update({"run": state}).eq("honeypot_id", honeypot).execute()

    def get_state(self, honeypot) -> APIResponse:
        response = self._client.table("state").select("*").eq("honeypot_id", honeypot).execute()
        return response

    def get_state_by_ip(self, ip) -> APIResponse:
        response = self._client.table("state").select("*").eq("ip", ip).execute()
        return response

    def set_honeypot_state(self, data) -> APIResponse:
        response = self.insert(table="state", data=data)
        return response


class NetworkConfDB(SupabaseHandler):
    def __init__(self) -> None:
        super().__init__()

    def save_conf(self, honeypot_id: str, conf: dict) -> APIResponse:
        if not self.get_network_conf(honeypot_id).data:
            print("record network not exists")
            return self.insert(table="network_conf", data={"honeypot_id": honeypot_id, "conf": conf})
        else:
            print("record network exists : ", self.get_network_conf(honeypot_id))
            return (self._client.table("network_conf").update({"honeypot_id": honeypot_id, "conf": conf})
                    .eq("honeypot_id", honeypot_id).execute())

    def get_network_conf(self, honeypot_id: str) -> APIResponse:
        response = self._client.table("network_conf").select("*").eq("honeypot_id", honeypot_id).execute()
        return response
