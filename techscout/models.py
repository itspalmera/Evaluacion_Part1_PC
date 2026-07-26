"""Modelos de datos del proyecto TechScout.

Define las entidades persistentes ProductType y Product usando SQLModel.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import validates
from sqlmodel import Field, Relationship, SQLModel


class ProductType(SQLModel, table=True):
    """Categoría o subcategoría de producto.

    Attributes:
        id: Identificador interno autogenerado.
        name: Nombre único de la subcategoría.
        products: Lista de productos asociados a este tipo.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)

    products: List["Product"] = Relationship(back_populates="type")

    @validates("name")
    def name_no_vacio(self, key: str, value: str) -> str:
        """Valida que el nombre del tipo de producto no esté vacío.

        Args:
            key: Nombre del atributo a validar.
            value: Valor propuesto.

        Returns:
            str: El valor sin espacios en los extremos.
        """
        if not value or not value.strip():
            raise ValueError("El nombre de ProductType no puede estar vacío.")
        return value.strip()


class Product(SQLModel, table=True):
    """Producto individual extraído del catálogo e-commerce.

    Attributes:
        id: Identificador interno autogenerado.
        product_id: Identificador extraído de la URL.
        title: Título descriptivo del producto.
        price_usd: Precio numérico en USD.
        scraped_at: Marca de tiempo de extracción.
        type_id: Clave foránea hacia ProductType.id.
        type: Instancia de ProductType asociada.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(index=True, unique=True, nullable=False)
    title: str = Field(nullable=False)
    price_usd: float = Field(nullable=False)
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type_id: Optional[int] = Field(default=None, foreign_key="producttype.id")

    type: Optional[ProductType] = Relationship(back_populates="products")

    @validates("product_id")
    def product_id_valido(self, key: str, value: int) -> int:
        """Valida que product_id sea mayor o igual a 1.

        Args:
            key: Nombre del atributo.
            value: Identificador propuesto.

        Returns:
            int: El valor validado.
        """
        if value < 1:
            raise ValueError("product_id debe ser mayor o igual a 1.")
        return value

    @validates("price_usd")
    def price_usd_valido(self, key: str, value: float) -> float:
        """Valida que price_usd sea mayor o igual a 0.0.

        Args:
            key: Nombre del atributo.
            value: Precio propuesto.

        Returns:
            float: El valor validado.
        """
        if value < 0.0:
            raise ValueError("price_usd debe ser mayor o igual a 0.0.")
        return value

    @validates("title")
    def title_no_vacio(self, key: str, value: str) -> str:
        """Valida que el título del producto no esté vacío.

        Args:
            key: Nombre del atributo.
            value: Título propuesto.

        Returns:
            str: Título sin espacios extra.
        """
        if not value or not value.strip():
            raise ValueError("El título del producto no puede estar vacío.")
        return value.strip()
