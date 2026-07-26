"""Modelos de datos del proyecto TechScout.

Define las entidades persistentes ``ProductType`` y ``Product`` usando SQLModel.
Ambas tablas están relacionadas mediante la clave foránea ``Product.type_id`` -> ``ProductType.id``
y la relación es navegable en ambos sentidos gracias a ``Relationship(back_populates=...)``.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import validates
from sqlmodel import Field, Relationship, SQLModel


class ProductType(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)

    products: List["Product"] = Relationship(back_populates="type")

    @validates("name")
    def name_no_vacio(self, key: str, value: str) -> str:

        if not value or not value.strip():
            raise ValueError("El nombre de ProductType no puede estar vacío.")
        return value.strip()


class Product(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(index=True, unique=True, nullable=False)
    title: str = Field(nullable=False)
    price_usd: float = Field(nullable=False)
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type_id: Optional[int] = Field(default=None, foreign_key="producttype.id")

    type: Optional[ProductType] = Relationship(back_populates="products")

    @validates("product_id")
    def product_id_valido(self, key: str, value: int) -> int:

        if value < 1:
            raise ValueError("product_id debe ser mayor o igual a 1.")
        return value

    @validates("price_usd")
    def price_usd_valido(self, key: str, value: float) -> float:

        if value < 0.0:
            raise ValueError("price_usd debe ser mayor o igual a 0.0.")
        return value

    @validates("title")
    def title_no_vacio(self, key: str, value: str) -> str:

        if not value or not value.strip():
            raise ValueError("El título del producto no puede estar vacío.")
        return value.strip()