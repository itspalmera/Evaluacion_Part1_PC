"""Utilidades de conexión y creación del esquema de base de datos SQLite.

Centraliza la creación del motor de SQLAlchemy/SQLModel usado por el resto del proyecto.
"""

from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

# IMPORTANTE: Importar los modelos aquí registra sus clases en SQLModel.metadata 
# para que create_db_and_tables() sepa qué tablas debe crear.
from techscout.models import Product, ProductType  # noqa: F401

DEFAULT_DB_PATH = Path("data/processed/techscout.db")


def get_engine(db_path: Path = DEFAULT_DB_PATH) -> Engine:
    """Crea o reutiliza la configuración del motor de base de datos SQLite.

    Args:
        db_path: Ruta al archivo SQLite usado como base de datos.
            Por defecto apunta a ``data/processed/techscout.db``.

    Returns:
        Engine: Instancia del motor de SQLAlchemy configurada para SQLite.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url, echo=False)


def create_db_and_tables(engine: Engine) -> None:
    """Crea todas las tablas definidas en SQLModel.metadata (y sus relaciones).

    Args:
        engine: Motor de base de datos sobre el que se crearán las tablas.

    Returns:
        None.
    """
    SQLModel.metadata.create_all(engine)