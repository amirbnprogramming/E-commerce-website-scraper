from date_section_scrapper import date_section
from file_utils.csv_saver import csv_saver
from file_utils.directory_creator import directory_creator
from product_scrapper import new_product_scrapper
from python_utils.bs4_utils import Browser
from python_utils.constants import new_products_url
from python_utils.logger import logger


def new_products_scrapper():
    browser = Browser()
    saved_products = {}
    unique_id = 1

    # make Chrome window
    browser = Browser()

    logger.warning("Start scraping (New Products Page)")
    directory = directory_creator('../csv/new_products/')

    soup = browser.get_soup(new_products_url)

    sections = soup.select("li.np-postlist__item")
    if len(sections) > 0:

        for section in sections:
            saved_products = {}
            unique_id = 1
            # region: Date Section
            section_date, section_title, section_items_count, section_description = date_section(section)
            # endregion: Date Section

            # region: Products Section
            products_list = section.find_all("li", class_="product-grid__item")
            for item in products_list:
                saved_products[unique_id] = new_product_scrapper(item, section_date)
                if saved_products[unique_id] is not None:
                    unique_id += 1
                else:
                    del saved_products[unique_id]
            # endregion: Products Section
            csv_saver(saved_products, directory + f'{section_date}', unique_id - 1)

    else:
        logger.warning("Page Not Found")
