import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = 'logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=True)
    source_ip: Mapped[str] = mapped_column(String, nullable=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=True)
    data: Mapped[str] = mapped_column(Text, nullable=True)
    dest_port: Mapped[int] = mapped_column(Integer, nullable=True)
    dest_ip: Mapped[str] = mapped_column(String, nullable=True)
    protocol: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SSHLog(Base):
    __tablename__ = 'ssh_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_ip: Mapped[str] = mapped_column(String, nullable=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=True)
    dest_ip: Mapped[str] = mapped_column(String, nullable=True)
    dest_port: Mapped[int] = mapped_column(Integer, nullable=True)
    command: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HTTPLog(Base):
    __tablename__ = 'http_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_ip: Mapped[str] = mapped_column(String, nullable=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=True)
    dest_ip: Mapped[str] = mapped_column(String, nullable=True)
    dest_port: Mapped[int] = mapped_column(Integer, nullable=True)
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModuleConf(Base):
    __tablename__ = 'modules_conf'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module: Mapped[str] = mapped_column(String, nullable=True)
    conf: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class State(Base):
    __tablename__ = 'state'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    honeypot_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    ip: Mapped[str] = mapped_column(String, nullable=True)
    run: Mapped[bool] = mapped_column(Boolean, default=False)
    extra: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NetworkConf(Base):
    __tablename__ = 'network_conf'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    honeypot_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    conf: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TelnetLog(Base):
    __tablename__ = 'telnet_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_ip: Mapped[str] = mapped_column(String, nullable=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=True)
    dest_ip: Mapped[str] = mapped_column(String, nullable=True)
    dest_port: Mapped[int] = mapped_column(Integer, nullable=True)
    command: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FTPLog(Base):
    __tablename__ = 'ftp_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_ip: Mapped[str] = mapped_column(String, nullable=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=True)
    event: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    filename: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BlockedIP(Base):
    __tablename__ = 'blocked_ips'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
