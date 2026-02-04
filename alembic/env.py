import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Импортируйте ваш Base.metadata, чтобы Alembic видел модели
# Замените 'src.infrastructure.database' на ваш реальный путь
from src.infrastructure.db.models.base import Base

# Это объект конфигурации Alembic
config = context.config

# Интерпретируем конфиг-файл для логирования
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
    # Проверяем, существует ли уже таблица из вашей первой миграции
    # Замените 'users' или 'orders' на имя любой вашей реальной таблицы
    from sqlalchemy import inspect

    inspector = inspect(connection)
    tables = inspector.get_table_names()

    # Если таблицы уже есть, а таблицы alembic_version нет
    if "orders" in tables and "alembic_version" not in tables:
        # Маркируем базу как "уже на последней версии" без выполнения кода миграций
        context.configure(connection=connection, target_metadata=target_metadata)
        context.get_context()._stamp(context.get_current_revision(), "head")
        print(
            "Database tables already exist. Stamping head without running migrations."
        )
        return  # Выходим, не запуская миграции, которые вызывают ошибку

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
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
