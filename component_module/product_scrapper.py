from python_utils.bs4_utils import Browser
from python_utils.constants import baseurl
from python_utils.logger import logger


def link_scrapper(item):
    try:
        link = baseurl + item.find('a', href=True)['href']
    except Exception:
        link = None

    return link


def product_detailer_page(soup):
    # region:title
    try:
        title = soup.select('span.breadcrumb__link')[-1].text.strip()
    except IndexError:
        return None
    # endregion:title

    # region:brand
    try:
        brand = soup.select('li.breadcrumb__item a')[-1].text.strip()
    except  AttributeError or IndexError:
        brand = None
    # endregion:brand

    # region:category
    try:
        category = soup.select('li.breadcrumb__item')[2].text.strip().replace(" ", "_")
    except  AttributeError or IndexError:
        category = None
    # endregion:category

    # region:percentages
    try:
        percentages = soup.select_one('p.product-main__data').text.strip()
    except  AttributeError or IndexError:
        percentages = None
    # endregion:percentages

    # region:star_rating
    try:
        rating = soup.find('span', class_='review-overview__rating').text.strip()
    except  AttributeError or IndexError:
        rating = None
    # endregion:star_rating

    # region: stock_flag
    try:
        stock_flag = soup.find('p', class_='product-atb__stock-flag').text.strip()
    except  AttributeError or IndexError:
        stock_flag = None
    # endregion: stock_flag

    # region: price
    try:
        price = soup.find('p', class_='product-action__price').text.strip()
    except  AttributeError or IndexError:
        price = None
    # endregion: price

    # region: unit_price
    try:
        unit_price = soup.find('p', class_='product-action__unit-price').text.strip()
    except  AttributeError or IndexError:
        unit_price = None
    # endregion: unit_price

    # region: description_text
    try:
        description_text = soup.select_one('div.product-main__description p').text.replace('\n', '')
    except  AttributeError or IndexError:
        description_text = None
    # endregion: description_text

    # region: style
    try:
        style_detail = {}
        style_section = soup.find_all('li', class_='flavour-profile__item flavour-profile__item--style')
        if len(style_section) == 0:
            raise AttributeError
        for items in style_section:
            lable = items.find('span', class_='flavour-profile__label').text.strip().lower()
            rating = items.find('span', class_='flavour-profile__content').text.strip().lower()
            style_detail[lable] = rating
    except  AttributeError or IndexError:
        style_detail = None
    # endregion: style

    # region: character
    try:
        character_detail = []
        character_section = soup.find_all('li', class_="flavour-profile__item flavour-profile__item--character")
        if len(character_section) == 0:
            raise AttributeError
        for items in character_section:
            label = items.find('span', class_='flavour-profile__label').text.strip().lower()
            character_detail.append(label)
    except  AttributeError or IndexError:
        character_detail = None
    # endregion: character

    # region: facts
    try:
        facts_detail = {}
        fact_section = soup.find_all('li', class_="product-facts__item")
        if len(fact_section) == 0:
            raise AttributeError
        for items in fact_section:
            label = items.find('h3', class_='product-facts__type').text.strip().lower()
            data = items.find('p', class_='product-facts__data').text.strip().lower()
            facts_detail[label] = data
    except  AttributeError or IndexError:
        facts_detail = None
    # endregion: facts

    # region:image
    try:
        image_section = soup.find('img', class_='product-main__image')
        if image_section is None:
            image_link = soup.find('img', class_='product-slider__image')['src']
            image_alt = soup.find('img', class_='product-slider__image')['alt']
        else:
            image_link = soup.find('img', class_='product-main__image')['src']
            image_alt = soup.find('img', class_='product-main__image')['alt']

    except  AttributeError or IndexError:
        image_link = None
        image_alt = None
    # endregion:image

    return title, brand, category, percentages, rating, stock_flag, price, unit_price, description_text, style_detail, character_detail, facts_detail, image_link, image_alt


def product_scrapper(browser: Browser, item):
    saved_product = {}
    # region: product list page
    link = link_scrapper(item)
    # endregion:product list page

    # region: product detail page
    product_page_soup = browser.get_soup(link)
    product_page_result = product_detailer_page(product_page_soup)
    if product_page_result is not None:
        title, brand, category, percentages, rating, stock_flag, price, unit_price, description_text, style_detail, character_detail, facts_detail, image_link, image_alt = product_page_result
        # region: Saving
        saved_product = {
            'product_title': title,
            'product_details': {
                'brand': brand,
                'category': category,
                'link': link,
                'image_detail': {
                    'image_link': image_link,
                    'image_alt': image_alt
                },
                'rating': rating,
                'percentages': percentages,
                'availability': stock_flag,
                'price': price,
                'unit_price': unit_price,
                'description': description_text,
                'style': style_detail,
                'characters': character_detail,
                'facts': facts_detail,
            }
        }
        # endregion: Saving

        # region:Telegram notify


        # endregion:Telegram notify

        logger.warning(f"Product ({title}) is Saved.")

        return saved_product

    else:
        logger.warning(f"Product Not Found.")
        return None


def new_product_scrapper(browser: Browser, item, section_date):
    saved_product = {}
    # region: product list page
    link = link_scrapper(item)
    # endregion:product list page

    # region: product detail page
    product_page_soup = browser.get_soup(link)
    product_page_result = product_detailer_page(product_page_soup)
    if product_page_result is not None:
        title, brand, category, percentages, rating, stock_flag, price, unit_price, description_text, style_detail, character_detail, facts_detail, image_link, image_alt = product_page_result
        # region: Saving
        saved_product = {
            'release_date': section_date,
            'product_title': title,
            'product_details': {
                'brand': brand,
                'category': category,
                'link': link,
                'image_detail': {
                    'image_link': image_link,
                    'image_alt': image_alt
                },
                'rating': rating,
                'percentages': percentages,
                'availability': stock_flag,
                'price': price,
                'unit_price': unit_price,
                'description': description_text,
                'style': style_detail,
                'characters': character_detail,
                'facts': facts_detail,
            }
        }
        # endregion: Saving

        logger.warning(f"Product ({title}) is Saved.")

        return saved_product

    else:
        logger.warning(f"Product Not Found.")
        return None
