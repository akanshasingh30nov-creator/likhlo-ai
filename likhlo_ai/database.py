from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from likhlo_ai.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug
)


# Enforce SQLite performance and integrity pragmas (WAL mode, foreign keys)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize all database tables in SQLite WAL mode."""
    from likhlo_ai import models  # Ensure models are loaded
    Base.metadata.create_all(bind=engine)
