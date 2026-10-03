"""Database engine, session management, and table creation."""
import logging
import os
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)

# Retrieve database connection string from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./product_catalog.db",
)

# Normalize postgres:// to postgresql:// for SQLAlchemy 1.4+ / 2.0+ compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requires connect_args check_same_thread=False
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# Initialize SQLAlchemy / SQLModel engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)


def create_db_and_tables() -> None:
    """Create all database tables registered in SQLModel metadata."""
    logger.info("Running SQLModel.metadata.create_all...")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency function yielding a database session per HTTP request."""
    with Session(engine) as session:
        yield session
