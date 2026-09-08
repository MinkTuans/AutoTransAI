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

is_sqlite = db_url.startswith("sqlite")
is_mysql = "mysql" in db_url

if is_sqlite:
    _ensure_db_directory()

connect_args = {}
engine_kwargs = {"echo": settings.DEBUG}

if is_sqlite:
    connect_args["check_same_thread"] = False
elif is_mysql:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 3600
    connect_args["connect_timeout"] = 5

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
    tables_map = {t.lower(): t for t in inspector.get_table_names()}
    is_pg = sync_conn.dialect.name.startswith("postgres")
    is_my = sync_conn.dialect.name.startswith("mysql")

    for table_name, table_obj in Base.metadata.tables.items():
        matched_real_table = tables_map.get(table_name.lower())
        if not matched_real_table:
            continue

        try:
            existing_cols = {col["name"].lower(): col for col in inspector.get_columns(matched_real_table)}
        except Exception:
            existing_cols = {}

        for col_name, column_obj in table_obj.columns.items():
            real_col_name = column_obj.name or col_name
            if real_col_name.lower() in existing_cols:
                continue

            col_type_sql = column_obj.type.compile(sync_conn.dialect)

            if is_pg:
                alter_sql = f'ALTER TABLE "{matched_real_table}" ADD COLUMN IF NOT EXISTS "{real_col_name}" {col_type_sql}'
            elif is_my:
                default_clause = ""
                if column_obj.default is not None and hasattr(column_obj.default, "arg"):
                    arg = column_obj.default.arg
                    if isinstance(arg, (str, int, float, bool)):
                        default_clause = f" DEFAULT '{arg}'" if isinstance(arg, str) else f" DEFAULT {arg}"
                alter_sql = f'ALTER TABLE `{matched_real_table}` ADD COLUMN `{real_col_name}` {col_type_sql}{default_clause}'
            else:
                default_clause = ""
                if column_obj.default is not None and hasattr(column_obj.default, "arg"):
                    arg = column_obj.default.arg
                    if isinstance(arg, (str, int, float, bool)):
                        default_clause = f" DEFAULT '{arg}'" if isinstance(arg, str) else f" DEFAULT {arg}"
                alter_sql = f'ALTER TABLE "{matched_real_table}" ADD COLUMN "{real_col_name}" {col_type_sql}{default_clause}'

            try:
                if is_pg:
                    sync_conn.exec_driver_sql("SAVEPOINT sp_col_add")
                sync_conn.exec_driver_sql(alter_sql)
                if is_pg:
                    sync_conn.exec_driver_sql("RELEASE SAVEPOINT sp_col_add")
                logger.info(f"Added column '{real_col_name}' to table '{matched_real_table}' via DDL")
            except Exception as ex:
                if is_pg:
                    try:
                        sync_conn.exec_driver_sql("ROLLBACK TO SAVEPOINT sp_col_add")
                    except Exception:
                        pass
                logger.error(f"Failed adding column '{real_col_name}' to table '{matched_real_table}': {str(ex)}")



async def init_db() -> None:
    """Create all tables and run dialect-agnostic schema migrations."""
    global engine, async_session_factory, is_sqlite, is_mysql, is_postgres
    import logging
    logger = logging.getLogger("app.database")

    await engine.dispose()
    try:
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
    except Exception as ex:
        if is_mysql:
            logger.warning(f"MySQL connection failed ({str(ex)}). Falling back to local SQLite database...")
            fallback_db_url = f"sqlite+aiosqlite:///{settings.DATA_DIR / settings.DB_FILENAME}"
            _ensure_db_directory()
            engine = create_async_engine(fallback_db_url, connect_args={"check_same_thread": False})
            async_session_factory.configure(bind=engine)
            is_sqlite = True
            is_mysql = False
            async with engine.begin() as conn:
                await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
                await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
                await conn.run_sync(Base.metadata.create_all)
                await conn.run_sync(_sync_schema_sync)
        else:
            raise ex





async def get_session() -> AsyncSession:  # type: ignore[misc]
    """Dependency injection for FastAPI routes."""
    async with async_session_factory() as session:
        yield session
