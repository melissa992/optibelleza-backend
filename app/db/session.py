from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Support Postgres (production) and a local SQLite fallback for demos/tests.
# Use APP_ENV to decide: production -> postgres when configured, otherwise sqlite.
hostname = (settings.database_hostname or "").strip()
app_env = (settings.app_env or "").lower()
use_sqlite = (
    hostname == "sqlite"
    or not hostname
    or app_env not in ("production", "prod")
)
if use_sqlite:
    # Development / local / fallback: use a local file-based sqlite database.
    # On Vercel serverless, writeable storage is under /tmp.
    default_db_path = "/tmp/test2.db" if os.getenv("VERCEL") else "./test2.db"
    db_path = settings.database_name or default_db_path
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.abspath(db_path)}"
    # For SQLite, need check_same_thread=False when using with multiple threads.
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Production: use Postgres (credentials come from settings / .env)
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=10, max_overflow=20)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()