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
    """Ensure the database directory exists if using SQLite."""
    if settings.DB_URL.startswith("sqlite"):
        db_path = settings.DATA_DIR / settings.DB_FILENAME
        db_path.parent.mkdir(parents=True, exist_ok=True)


db_url = settings.DB_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

is_sqlite = db_url.startswith("sqlite")
is_postgres = "postgresql" in db_url

if is_sqlite:
    _ensure_db_directory()

connect_args = {}
engine_kwargs = {"echo": settings.DEBUG}

if is_sqlite:
    connect_args["check_same_thread"] = False
elif is_postgres:
    engine_kwargs["pool_pre_ping"] = True
    connect_args["statement_cache_size"] = 0
    connect_args["prepared_statement_cache_size"] = 0

engine = create_async_engine(
    db_url,
    connect_args=connect_args,
    **engine_kwargs
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
    is_pg = sync_conn.dialect.name.startswith("postgres")


    for table_name, table_obj in Base.metadata.tables.items():
        if table_name.lower() not in existing_tables:
            continue

        existing_cols = {col["name"].lower(): col for col in inspector.get_columns(table_name)}

        for col_name, column_obj in table_obj.columns.items():
            if col_name.lower() in existing_cols:
                continue

            col_type_sql = column_obj.type.compile(sync_conn.dialect)

            if is_pg:
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type_sql}"
            else:
                default_clause = ""
                if column_obj.default is not None and hasattr(column_obj.default, "arg"):
                    arg = column_obj.default.arg
                    if isinstance(arg, (str, int, float, bool)):
                        default_clause = f" DEFAULT '{arg}'" if isinstance(arg, str) else f" DEFAULT {arg}"
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type_sql}{default_clause}"

            try:
                sync_conn.exec_driver_sql(alter_sql)
                logger.info(f"Added column '{col_name}' to table '{table_name}' via DDL")
            except Exception as ex:
                logger.error(f"Failed adding column '{col_name}' to table '{table_name}': {str(ex)}")



async def init_db() -> None:
    """Create all tables and run dialect-agnostic schema migrations."""
    async with engine.begin() as conn:
        if is_sqlite:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
            await conn.exec_driver_sql("PRAGMA foreign_keys=ON")

        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as ex:
            if "already exists" not in str(ex).lower():
                raise ex

        # Run dynamic DDL schema migration across all dialects (Postgres, SQLite, MySQL)
        await conn.run_sync(_sync_schema_sync)





async def get_session() -> AsyncSession:  # type: ignore[misc]
    """Dependency injection for FastAPI routes."""
    async with async_session_factory() as session:
        yield session
