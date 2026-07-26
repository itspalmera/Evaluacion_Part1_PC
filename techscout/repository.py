"""Capa de persistencia del proyecto TechScout.

Maneja operaciones de inserción, actualización (upsert) y consulta mediante SQLModel.
"""

from typing import List, Sequence

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from techscout.models import Product, ProductType
from techscout.scraper import ScrapedProduct


class ProductRepository:
    """Repositorio de acceso a datos para productos y sus tipos.

    Attributes:
        engine: Motor de base de datos usado para instanciar las sesiones.
    """

    def __init__(self, engine: Engine) -> None:
        """Inicializa el repositorio con un motor de base de datos.

        Args:
            engine: Instancia de Engine configurada.

        Returns:
            None.
        """
        self.engine = engine

    def get_or_create_type(self, name: str) -> ProductType:
        """Busca un ProductType por nombre o lo crea si no existe.

        Args:
            name: Nombre de la subcategoría/tipo de producto.

        Returns:
            ProductType: Objeto ProductType persistido o existente.
        """
        with Session(self.engine) as session:
            statement = select(ProductType).where(ProductType.name == name)
            existing = session.exec(statement).first()
            if existing is not None:
                return existing

            product_type = ProductType(name=name)
            session.add(product_type)
            session.commit()
            session.refresh(product_type)
            return product_type

    def upsert_products(self, scraped_products: Sequence[ScrapedProduct]) -> None:
        """Inserta o actualiza productos vinculándolos a su tipo de producto.

        Args:
            scraped_products: Secuencia de objetos ScrapedProduct extraídos.

        Returns:
            None.
        """
        with Session(self.engine) as session:
            for item in scraped_products:
                type_stmt = select(ProductType).where(
                    ProductType.name == item.type_name
                )
                product_type = session.exec(type_stmt).first()
                if product_type is None:
                    product_type = ProductType(name=item.type_name)
                    session.add(product_type)
                    session.flush()

                statement = select(Product).where(Product.product_id == item.product_id)
                existing = session.exec(statement).first()

                if existing is not None:
                    existing.title = item.title
                    existing.price_usd = item.price_usd
                    existing.type_id = product_type.id
                    session.add(existing)
                else:
                    new_product = Product(
                        product_id=item.product_id,
                        title=item.title,
                        price_usd=item.price_usd,
                        type_id=product_type.id,
                    )
                    session.add(new_product)

            session.commit()

    def get_top_n(self, n: int) -> List[Product]:
        """Retorna los N productos más caros cargando la relación con ProductType.

        Args:
            n: Cantidad de productos a retornar.

        Returns:
            List[Product]: Lista de los N productos ordenados por precio descendente.
        """
        with Session(self.engine) as session:
            statement = select(Product).order_by(Product.price_usd.desc()).limit(n)
            products = session.exec(statement).all()
            for product in products:
                _ = product.type.name if product.type else None
            return list(products)

    def get_products_by_type(self, type_name: str) -> List[Product]:
        """Obtiene todos los productos correspondientes a un tipo dado.

        Args:
            type_name: Nombre del tipo/categoría de productos.

        Returns:
            List[Product]: Lista de productos asociados a ese tipo.
        """
        with Session(self.engine) as session:
            statement = select(ProductType).where(ProductType.name == type_name)
            product_type = session.exec(statement).first()
            if product_type is None:
                return []
            return list(product_type.products)
