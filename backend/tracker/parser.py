import time
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, StaleElementReferenceException

parser = 'lxml'

# blocks that contains tags and divs of dynamicly loaded provider
provider_element_classes = [
    'seller__name',
    'seller-details__title',
]

# url pattern with space for item vendor code
url_pattern = "https://www.wildberries.ru/catalog/{}/detail.aspx?targetUrl=MI"


def get_web_driver() -> webdriver.Chrome:
    """
    Getting selenium webdriver that make background browser operations
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    capabilities = options.to_capabilities()
    web_driver = webdriver.Remote(
        command_executor='http://hub:4444/wd/hub',
        desired_capabilities=capabilities,
    )
    return web_driver


def get_soup_parser(
        html: str,
        restrictive_class: str | None = "product-detail"
) -> BeautifulSoup:
    """
    Gets page html and restrictive class that needed to limit parsing zone inside this class, returns soup object
    """

    # All info that we need is contained in div with class product-detail so lets parse only from that div
    # Make parsing faster for about 40%
    div_containing_product_details = SoupStrainer(class_=restrictive_class)
    soup = BeautifulSoup(html, parser, parse_only=div_containing_product_details)

    return soup


def get_data(url: str) -> tuple | bool:
    """
    Gets html page including dynamically loaded by js content
    """

    # Get webdriver
    driver = get_web_driver()

    # Check if url is correct
    try:
        driver.get(url)
    except InvalidArgumentException:
        return False

    # Tries to find producer info or returns None if cannot find( it may be caused by wrong link )
    provider_elem_class = wait_for_elems(driver, provider_element_classes)

    # Getting html of page and destroying driver session
    html = driver.page_source
    driver.quit()

    return html, provider_elem_class


def extract_product_info(
        html: str,
        provider: str,
) -> dict[str, str]:
    """
    Extracts all info about product and return dict containing product info,
    exactly: price, sale price, brand, name, vendor  code
    """

    soup = get_soup_parser(html)
    product_price_with_sale = ''.join(soup.find('span', class_='price-block__final-price').text.strip().split()[:-1])

    # Check if out of order
    if product_price_with_sale == '':
        product_price_with_sale = 0

    # if there is no sale then produce price with sale is our price and product price will be none because there
    # is no block with class price-block__old-price
    try:
        product_price = ''.join(soup.find('del', class_='price-block__old-price').text.strip().split()[:-1])
    except AttributeError:
        product_price = product_price_with_sale

    brand_and_name = soup.find('h1', class_='same-part-kt__header').find_all('span')
    product_brand = brand_and_name[0].text.strip()
    product_name = brand_and_name[1].text.strip()

    product_vendor_code = soup.find('span', id='productNmId').text.strip()
    provider = provider.strip()

    product_detail = {
        'brand': product_brand,
        'name': product_name,
        'vendor_code': product_vendor_code,
        'price': product_price,
        'price_with_sale': product_price_with_sale,
        'provider': provider,
    }

    return product_detail


def wait_for_elems(
        driver: webdriver,
        elems_classes_with_tags_list: list,
) -> bool | str:
    """
    Functions that waits for one of the elements from list to be found on the page,
    if nothing found in 5 seconds or page contains 404 error then returns false
    """
    try:
        driver.find_element(By.CLASS_NAME, 'content404')
        return False
    except (NoSuchElementException, StaleElementReferenceException):
        start_time = time.time()
        time_now = time.time()
        while time_now - start_time < 5:
            for elem_class in elems_classes_with_tags_list:
                try:
                    element = driver.find_element(By.CLASS_NAME, elem_class)
                    return element.text
                except (NoSuchElementException, StaleElementReferenceException):
                    pass
            time.sleep(0.05)
            time_now = time.time()
    return False


def get_product_info(vendor_code: int | str) -> dict[str, str] | bool:
    """
    Parse wildberries product info by product url
    """

    # place vendor code into our url pattern
    url = url_pattern.format(vendor_code)
    html, provider = get_data(url)
    if html and provider:
        # getting product details
        product_detail = extract_product_info(html, provider)

        # writing data to output file
        return product_detail
    else:
        return False
