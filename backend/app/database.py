"""
Database engine and session management.

Uses SQLAlchemy 2.0 async with aiosqlite for SQLite.
WAL mode is enabled for better concurrent read performance.
"""

from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def _ensure_db_directory() -> None:
    """Ensure the database directory exists."""
    db_path = settings.DATA_DIR / settings.DB_FILENAME
    db_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_db_directory()

is_sqlite = settings.DB_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_async_engine(
    settings.DB_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
)


if is_sqlite:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable foreign key constraints for every SQLite connection."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)



def _sync_schema_sync(sync_conn):
    """
    Synchronously inspect tables and columns across any DB dialect (SQLite, MySQL, MariaDB, Postgres)
    and issue ALTER TABLE ADD COLUMN for any ORM columns missing in the active database.
    """
    from sqlalchemy import inspect
    import logging
    logger = logging.getLogger("app.database")

    inspector = inspect(sync_conn)
    existing_tables = set(inspector.get_table_names())

    for table_name, table_obj in Base.metadata.tables.items():
        if table_name not in existing_tables:
            continue

        existing_cols = {col["name"].lower(): col for col in inspector.get_columns(table_name)}

        for col_name, column_obj in table_obj.columns.items():
            if col_name.lower() in existing_cols:
                continue

            col_type_sql = column_obj.type.compile(sync_conn.dialect)
            default_clause = ""
            if column_obj.default is not None and hasattr(column_obj.default, "arg"):
                arg = column_obj.default.arg
                if isinstance(arg, (str, int, float, bool)):
                    default_clause = f" DEFAULT '{arg}'" if isinstance(arg, str) else f" DEFAULT {arg}"

            null_clause = " NULL" if column_obj.nullable else " NOT NULL"
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type_sql}{null_clause}{default_clause}"

            try:
                sync_conn.exec_driver_sql(alter_sql)
                logger.info(f"Added column '{col_name}' to table '{table_name}' via DDL")
            except Exception as ex1:
                try:
                    fallback_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type_sql}"
                    sync_conn.exec_driver_sql(fallback_sql)
                    logger.info(f"Added column '{col_name}' to table '{table_name}' via fallback DDL")
                except Exception as ex2:
                    logger.error(f"Failed adding column '{col_name}' to table '{table_name}': {str(ex2)}")


async def init_db() -> None:
    """Create all tables and run dialect-agnostic schema migrations."""
    async with engine.begin() as conn:
        if is_sqlite:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
            await conn.exec_driver_sql("PRAGMA foreign_keys=ON")

        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_sync_schema_sync)




async def get_session() -> AsyncSession:  # type: ignore[misc]
    """Dependency injection for FastAPI routes."""
    async with async_session_factory() as session:
        yield session
