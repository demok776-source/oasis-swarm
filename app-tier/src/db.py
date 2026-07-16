import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.utils.logger import get_logger

logger = get_logger("db_client")

DB_USER = os.getenv("DB_USER", "oasis_admin")
DB_NAME = os.getenv("DB_NAME", "oasis_db")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")

USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

# Previously this had `os.getenv("DB_PASS", "SecurePassword123!")` -- a
# real-looking, publicly-committed default password baked into source. Any
# misconfigured environment that forgot to set DB_PASS would silently
# connect with a well-known credential instead of failing. Postgres modes
# now require it explicitly; SQLite mode (local dev/tests) doesn't touch
# Postgres at all so it's exempt.
DB_PASS = os.getenv("DB_PASS")
if not USE_SQLITE and not DB_PASS:
    raise RuntimeError(
        "DB_PASS is not set. Set it via your .env file (see .env.example) or, in "
        "production, via GCP Secret Manager -- never hardcode a database password."
    )

# Unix socket configuration for Cloud SQL (project-f537c014-8ae2-4195-9f3:europe-west1:primary-db)
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME", "project-f537c014-8ae2-4195-9f3:europe-west1:primary-db")
UNIX_SOCKET_PATH = f"/cloudsql/{INSTANCE_CONNECTION_NAME}"

# Build SQLAlchemy connection URL
# On Cloud Run, we use Unix sockets. Otherwise we use TCP.

if USE_SQLITE:
    logger.info("Using SQLite database.")
    DATABASE_URL = "sqlite:///oasis_local.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
elif os.path.exists(UNIX_SOCKET_PATH) or os.getenv("KUBERNETES_SERVICE_HOST") is None and os.getenv("CLOUD_RUN_JOB") is not None or os.getenv("INSTANCE_CONNECTION_NAME"):
    logger.info(f"Connecting to database via Unix socket: {UNIX_SOCKET_PATH}")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={UNIX_SOCKET_PATH}"
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )
else:
    logger.info(f"Connecting to database via TCP: {DB_HOST}:{DB_PORT}")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
