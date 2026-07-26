"""Punto de entrada principal para el pipeline de TechScout."""

import logging

from techscout.db import create_db_and_tables, get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
