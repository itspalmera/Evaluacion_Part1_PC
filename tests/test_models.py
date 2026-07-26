"""Tests unitarios para las validaciones de los modelos ProductType y Product."""

import pytest

from techscout.models import Product, ProductType


def test_product_type_name_no_vacio() -> None:
    """ProductType.name no debe aceptar cadenas vacías o compuestas por espacios."""
    with pytest.raises(ValueError):
        ProductType(name="   ")


def test_product_type_valido() -> None:
    """Instanciación válida de ProductType."""
    product_type = ProductType(name="Laptops")
    assert product_type.name == "Laptops"


def test_product_id_invalido() -> None:
    """Product.product_id debe ser mayor o igual a 1."""
    with pytest.raises(ValueError):
        Product(product_id=0, title="Laptop de prueba", price_usd=500.0)


def test_product_price_negativo_invalido() -> None:
    """Product.price_usd no puede ser menor a 0.0."""
    with pytest.raises(ValueError):
        Product(product_id=1, title="Laptop de prueba", price_usd=-10.0)


def test_product_title_vacio_invalido() -> None:
    """Product.title no puede estar vacío."""
    with pytest.raises(ValueError):
        Product(product_id=1, title="   ", price_usd=100.0)


def test_product_valido() -> None:
    """Instanciación válida de la entidad Product."""
    product = Product(product_id=37, title="Asus ROG Gaming", price_usd=1200.50)
    assert product.product_id == 37
    assert product.title == "Asus ROG Gaming"
    assert product.price_usd == 1200.50
