"""Tests unitarios para ProductRepository utilizando una base de datos SQLite temporal."""

from pathlib import Path
from typing import Iterator

import pytest
from sqlalchemy.engine import Engine

from techscout.db import create_db_and_tables, get_engine
from techscout.repository import ProductRepository
from techscout.scraper import ScrapedProduct


@pytest.fixture()
def engine(tmp_path: Path) -> Iterator[Engine]:
    """Crea un motor SQLite temporal con el esquema de tablas inicializado.

    Args:
        tmp_path: Ruta al directorio temporal proporcionado por pytest.

    Yields:
        Iterator[Engine]: Instancia del motor de base de datos para los tests.
    """
    db_path = tmp_path / "test_techscout.db"
    test_engine = get_engine(db_path)
    create_db_and_tables(test_engine)
    yield test_engine


def test_get_or_create_type_no_duplica(engine: Engine) -> None:
    """Garantiza que llamar dos veces a get_or_create_type no cree registros duplicados."""
    repository = ProductRepository(engine)
    first = repository.get_or_create_type("Laptops")
    second = repository.get_or_create_type("Laptops")
    assert first.id == second.id


def test_upsert_products_no_duplica(engine: Engine) -> None:
    """Garantiza que upsert_products omita productos duplicados por product_id."""
    repository = ProductRepository(engine)
    items = [
        ScrapedProduct(
            product_id=1, title="Laptop A", type_name="Laptops", price_usd=800.0
        )
    ]

    repository.upsert_products(items)
    repository.upsert_products(items)

    products = repository.get_products_by_type("Laptops")
    assert len(products) == 1


def test_get_top_n(engine: Engine) -> None:
    """Verifica que get_top_n ordene por precio descendente y cargue la relación con su tipo."""
    repository = ProductRepository(engine)
    items = [
        ScrapedProduct(
            product_id=1, title="Barata", type_name="Laptops", price_usd=300.0
        ),
        ScrapedProduct(
            product_id=2, title="Cara", type_name="Laptops", price_usd=1500.0
        ),
        ScrapedProduct(
            product_id=3, title="Media", type_name="Laptops", price_usd=700.0
        ),
    ]
    repository.upsert_products(items)

    top_2 = repository.get_top_n(2)
    assert [p.title for p in top_2] == ["Cara", "Media"]
    assert top_2[0].type is not None
    assert top_2[0].type.name == "Laptops"


def test_get_products_by_type_inexistente(engine: Engine) -> None:
    """Verifica que get_products_by_type devuelva una lista vacía si la categoría no existe."""
    repository = ProductRepository(engine)
    assert repository.get_products_by_type("Inexistente") == []
