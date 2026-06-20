from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import inspect, select, update as sa_update, delete as sa_delete

from src.db.engine import get_session
from src.db.models import Account, Log, SSHLog, HTTPLog, ModuleConf, State, NetworkConf
from src.network.utils import check_password


@dataclass
class DBResult:
    """Mimics the subset of the Supabase APIResponse shape (.data) that the rest of the app relies on."""
    data: list = field(default_factory=list)


def _row_to_dict(row) -> dict:
    return {c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs}


class PostgresHandler:
    model = None

    def fetch_all(self, table: Optional[str] = None) -> DBResult:
        with get_session() as session:
            rows = session.execute(select(self.model)).scalars().all()
            return DBResult(data=[_row_to_dict(r) for r in rows])

    def fetch(self, table: Optional[str] = None, column: Optional[str] = None) -> DBResult:
        return self.fetch_all()

    def insert(self, table: Optional[str], data: dict) -> DBResult:
        with get_session() as session:
            row = self.model(**data)
            session.add(row)
            session.commit()
            session.refresh(row)
            return DBResult(data=[_row_to_dict(row)])

    def update(self, table: Optional[str], data: dict) -> DBResult:
        with get_session() as session:
            session.execute(sa_update(self.model).values(**data))
            session.commit()
            return DBResult(data=[])

    def delete(self, table: Optional[str], key: Optional[str] = None) -> DBResult:
        with get_session() as session:
            session.execute(sa_delete(self.model))
            session.commit()
            return DBResult(data=[])


class HoneyPotHandler(PostgresHandler):
    model = Log

    def fetch_all_logs(self) -> DBResult:
        return self.fetch_all()

    def add_log(self, log: dict) -> DBResult:
        return self.insert(table='logs', data=log)


class SSHServerCommandHandler(PostgresHandler):
    model = SSHLog

    def fetch_all_logs(self) -> DBResult:
        return self.fetch_all()

    def add_log(self, log: dict) -> DBResult:
        return self.insert(table='ssh_logs', data=log)


class HTTPServerDB(PostgresHandler):
    model = HTTPLog

    def fetch_all_logs(self) -> DBResult:
        return self.fetch_all()

    def add_log(self, log: dict) -> DBResult:
        return self.insert(table='http_logs', data=log)


class AccountDB(PostgresHandler):
    model = Account

    def _find_account(self, column: str, value: str) -> DBResult:
        with get_session() as session:
            rows = session.execute(
                select(Account).where(getattr(Account, column) == value)
            ).scalars().all()
            return DBResult(data=[_row_to_dict(r) for r in rows])

    def verify_user_credentials(self, username: str, password: str) -> bool:
        result = self._find_account('user', username)
        if not result.data:
            return False
        return check_password(result.data[0]['password'].encode(), password)

    def get_hp_name(self, username: str) -> DBResult:
        return self._find_account('user', username)

    def get_account(self, name: str) -> DBResult:
        return self._find_account('name', name)

    def get_account_by_username(self, username: str) -> DBResult:
        return self._find_account('user', username)


class ModuleConfDB(PostgresHandler):
    model = ModuleConf

    def post_conf_json(self, conf: dict) -> DBResult:
        return self.insert(table='modules_conf', data={'module': conf.get('module'), 'conf': conf})


class StateDB(PostgresHandler):
    model = State

    def change_run_state(self, state: bool, honeypot) -> DBResult:
        with get_session() as session:
            session.execute(
                sa_update(State).where(State.honeypot_id == honeypot).values(run=state)
            )
            session.commit()
            return DBResult(data=[])

    def get_state(self, honeypot) -> DBResult:
        with get_session() as session:
            rows = session.execute(
                select(State).where(State.honeypot_id == honeypot)
            ).scalars().all()
            return DBResult(data=[_row_to_dict(r) for r in rows])

    def get_state_by_ip(self, ip) -> DBResult:
        with get_session() as session:
            rows = session.execute(select(State).where(State.ip == ip)).scalars().all()
            return DBResult(data=[_row_to_dict(r) for r in rows])

    def set_honeypot_state(self, data: dict) -> DBResult:
        known_fields = {'honeypot_id', 'ip', 'run'}
        row_data = {k: v for k, v in data.items() if k in known_fields}
        row_data['extra'] = {k: v for k, v in data.items() if k not in known_fields}
        return self.insert(table='state', data=row_data)


class NetworkConfDB(PostgresHandler):
    model = NetworkConf

    def save_conf(self, honeypot_id: str, conf: dict) -> DBResult:
        existing = self.get_network_conf(honeypot_id)
        if not existing.data:
            print("record network not exists")
            return self.insert(table='network_conf', data={'honeypot_id': honeypot_id, 'conf': conf})
        else:
            print("record network exists : ", existing)
            with get_session() as session:
                session.execute(
                    sa_update(NetworkConf)
                    .where(NetworkConf.honeypot_id == honeypot_id)
                    .values(conf=conf)
                )
                session.commit()
                return self.get_network_conf(honeypot_id)

    def get_network_conf(self, honeypot_id: str) -> DBResult:
        with get_session() as session:
            rows = session.execute(
                select(NetworkConf).where(NetworkConf.honeypot_id == honeypot_id)
            ).scalars().all()
            return DBResult(data=[_row_to_dict(r) for r in rows])
