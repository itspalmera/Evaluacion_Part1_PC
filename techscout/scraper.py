"""Scraper para Web Scraper Test Sites - E-commerce (static).

Recorre el catálogo paginado usando Selenium en modo headless.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

BASE_URL = "https://webscraper.io/test-sites/e-commerce/static"
CARD_SELECTOR = "div.card.thumbnail, .card.thumbnail"
DEFAULT_TIMEOUT = 10


@dataclass
class ScrapedProduct:
    """Representa un producto crudo extraído de una tarjeta del catálogo.

    Attributes:
        product_id: Identificador numérico del producto extraído de la URL.
        title: Título o nombre del producto.
        type_name: Nombre de la subcategoría.
        price_usd: Precio numérico limpio en USD.
    """

    product_id: int
    title: str
    type_name: str
    price_usd: float


def _build_driver(headless: bool = True) -> webdriver.Chrome:
    """Construye e inicializa una instancia de Chrome WebDriver.

    Args:
        headless: Si es True, ejecuta el navegador sin interfaz gráfica.

    Returns:
        webdriver.Chrome: Instancia de Chrome configurada.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def _extract_product_id(card: WebElement) -> Optional[int]:
    """Extrae el product_id numérico desde el enlace del producto en la tarjeta.

    Args:
        card: Elemento WebElement de la tarjeta del producto.

    Returns:
        Optional[int]: Identificador numérico extraído o None.
    """
    link = card.find_element(By.CSS_SELECTOR, "a.title")
    href = link.get_attribute("href") or ""
    match = re.search(r"/product/(\d+)", href)
    return int(match.group(1)) if match else None


def _clean_price(raw_price: str) -> float:
    """Limpia el texto del precio eliminando el símbolo '$' y convirtiéndolo a float.

    Args:
        raw_price: Texto del precio tal como aparece en el sitio.

    Returns:
        float: Valor numérico flotante.
    """
    cleaned = raw_price.replace("$", "").replace(",", "").strip()
    return float(cleaned)


def _parse_card(card: WebElement, subcategory_name: str) -> ScrapedProduct:
    """Extrae los atributos requeridos de una tarjeta individual de producto.

    Args:
        card: Elemento WebElement de la tarjeta (.card.thumbnail).
        subcategory_name: Nombre de la subcategoría que se está recorriendo.

    Returns:
        ScrapedProduct: Objeto de datos con la información limpia.
    """
    product_id = _extract_product_id(card)
    if product_id is None:
        raise ValueError("No se pudo obtener product_id desde el enlace.")

    title_element = card.find_element(By.CSS_SELECTOR, "a.title")
    title = title_element.text.strip() or title_element.get_attribute("title") or ""

    price_element = card.find_element(By.CSS_SELECTOR, "span[itemprop='price']")
    price_usd = _clean_price(price_element.text)

    return ScrapedProduct(
        product_id=product_id,
        title=title,
        type_name=subcategory_name,
        price_usd=price_usd,
    )


def scrape_subcategory(
    subcategory_path: str = "computers/laptops",
    num_pages: int = 5,
    headless: bool = True,
) -> List[ScrapedProduct]:
    """Recorre al menos N páginas de una subcategoría y devuelve los productos.

    Args:
        subcategory_path: Ruta relativa de la subcategoría.
        num_pages: Número de páginas a recorrer.
        headless: Si es True, ejecuta en modo headless.

    Returns:
        List[ScrapedProduct]: Lista consolidada de productos extraídos.
    """
    driver = _build_driver(headless=headless)
    all_products: List[ScrapedProduct] = []
    subcategory_name = subcategory_path.split("/")[-1].capitalize()

    try:
        for page in range(1, num_pages + 1):
            url = f"{BASE_URL}/{subcategory_path}?page={page}"
            logger.info("Scrapeando página %d: %s", page, url)
            driver.get(url)

            wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
            try:
                wait.until(
                    ec.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, CARD_SELECTOR)
                    )
                )
            except TimeoutException:
                logger.warning("Timeout esperando tarjetas en la página %d.", page)
                continue

            try:
                active_menu = driver.find_element(
                    By.CSS_SELECTOR, "#side-menu a.active, .sidebar a.active"
                )
                if active_menu.text.strip():
                    subcategory_name = active_menu.text.strip()
            except NoSuchElementException:
                pass

            cards = driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR)

            for index, card in enumerate(cards):
                try:
                    product = _parse_card(card, subcategory_name)
                    all_products.append(product)
                except (NoSuchElementException, ValueError) as exc:
                    logger.warning(
                        "Error al procesar tarjeta #%d pág. %d: %s",
                        index + 1,
                        page,
                        exc,
                    )
                    continue

    finally:
        driver.quit()

    return all_products
