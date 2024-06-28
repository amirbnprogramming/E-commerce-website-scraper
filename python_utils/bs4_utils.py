import random
import time

from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome
from python_utils.logger import logger


class Browser(object):
    def __init__(self, ):
        self.driver = Chrome()

    def get_source(self, url):
        page_source = None
        logger.info(f"Sending request to ({url})")
        try:
            self.driver.get(url)
            time.sleep(random.randint(15, 35))
            page_source = self.driver.page_source
        except  Exception as e:
            logger.error(f"Request Failed ")
            page_source = None
        finally:
            return page_source

    def get_soup(self, url):
        response_text = self.get_source(url)
        if response_text is not None:
            soup = BeautifulSoup(response_text, "html.parser")
            return soup
        else:
            return None

    def close_driver(self):
        self.driver.close()
