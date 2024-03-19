import os
from postgrest import APIResponse
from supabase import create_client, Client
from dataclasses import dataclass


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
