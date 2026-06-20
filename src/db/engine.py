import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def _database_url() -> str:
    url = os.environ.get('DATABASE_URL')
    if url:
        return url
    user = os.environ.get('POSTGRES_USER')
    password = os.environ.get('POSTGRES_PASSWORD')
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    port = os.environ.get('POSTGRES_PORT', '5432')
    db = os.environ.get('POSTGRES_DB')
    if not (user and password and db):
        raise RuntimeError(
            "Missing database configuration: set DATABASE_URL, or "
            "POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB (+ optional POSTGRES_HOST/POSTGRES_PORT)"
        )
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_database_url(), future=True)
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), future=True)
    return _SessionLocal()
