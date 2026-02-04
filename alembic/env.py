import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool, inspect, text
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context


from src.infrastructure.db.models.base import Base

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    """Логика получения и обработки URL, такая же как в классе Database"""
    url = os.environ.get("POSTGRES_CONNECTION_STRING", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):

    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()

    if "orders" in existing_tables and "alembic_version" not in existing_tables:
        print("INFO: База уже создана. Выполняю ручной stamp версии 19203a8c2b9e...")

        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version ("
                "version_num VARCHAR(32) NOT NULL, "
                "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
                ")"
            )
        )

        current_rev = "19203a8c2b9e"
        connection.execute(
            text(f"INSERT INTO alembic_version (version_num) VALUES ('{current_rev}')")
        )
        print(f"INFO: База помечена ревизией {current_rev}. Пропускаю создание таблиц.")
        return

    # Если всё чисто, запускаем миграции как обычно
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме (асинхронно)."""

    # Создаем конфигурацию для движка программно
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run_sync запускает синхронную функцию do_run_migrations в асинхронном контексте
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Запуск асинхронного цикла
    try:
        asyncio.run(run_migrations_online())
    except (KeyboardInterrupt, SystemExit):
        pass
