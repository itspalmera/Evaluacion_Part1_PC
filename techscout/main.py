"""Punto de entrada principal para el pipeline de TechScout."""

import logging

from techscout.db import create_db_and_tables, get_engine
from techscout.repository import ProductRepository
from techscout.scraper import scrape_subcategory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run(num_pages: int = 5) -> None:
    """Ejecuta el pipeline completo: scraping, persistencia y consultas.

    Args:
        num_pages: Número de páginas de la subcategoría a recorrer.

    Returns:
        None.
    """
    engine = get_engine()
    create_db_and_tables(engine)

    logger.info("Iniciando scraping de %d páginas de Laptops...", num_pages)
    scraped_data = scrape_subcategory(
        subcategory_path="computers/laptops", num_pages=num_pages, headless=True
    )
    logger.info("Se extrajeron %d productos en total.", len(scraped_data))

    repository = ProductRepository(engine)
    repository.upsert_products(scraped_data)
    logger.info("Productos persistidos correctamente en la base de datos.")

    logger.info("=== TOP 5 PRODUCTOS MÁS CAROS ===")
    top_products = repository.get_top_n(5)
    for prod in top_products:
        cat_name = prod.type.name if prod.type else "Sin tipo"
        logger.info(" - %s (%s): $%.2f USD", prod.title, cat_name, prod.price_usd)

    if top_products and top_products[0].type:
        sample_type = top_products[0].type.name
        by_type = repository.get_products_by_type(sample_type)
        logger.info("=== PRODUCTOS PERTENECIENTES A '%s': %d ===", sample_type, len(by_type))
        for prod in by_type[:5]:
            logger.info(" - %s: $%.2f USD", prod.title, prod.price_usd)


if __name__ == "__main__":
    run()