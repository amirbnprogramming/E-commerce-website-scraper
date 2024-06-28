import functools
import os
import random
import threading

import pandas as pd
import telebot
from bs4 import BeautifulSoup

from component_module.date_section_scrapper import date_section
from component_module.product_scrapper import product_scrapper, new_product_scrapper

from file_utils.csv_saver import csv_main_items_saver, csv_saver, csv_brand_saver
from file_utils.directory_creator import directory_creator

from python_utils.bs4_utils import Browser
from python_utils.constants import by_brand_url, items_type, baseurl, all_offers_url, new_products_url, API_TOKEN, \
    markup
from python_utils.get_time import get_time
from python_utils.logger import logger

# region :Bot creating
bot = telebot.TeleBot(API_TOKEN)


# endregion :Bot creating


class TelegramScrapper:
    def __init__(self):
        self.link_button = telebot.types.InlineKeyboardButton(text='More Info')
        self.chat_id = None
        self.browser = None
        self.welcome_logo = None

    @staticmethod
    def print_function_start(name, dir_name):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                bot.send_message(tele_scrapper.chat_id, f"🟢 Scraping ({name}) Started . . .")
                bot.send_message(tele_scrapper.chat_id, 'Bot is Working .... be patient 🙏')

                logger.info(f" Scraping ({name}) Started . . .")

                directory = directory_creator(f'../csv/{dir_name}/')

                func(*args, **kwargs, directory=directory)

                bot.send_photo(tele_scrapper.chat_id,
                               photo=tele_scrapper.welcome_logo,
                               caption="🔎 Welcome to Scraper Manager of Site (Thewhisky Exchange)",
                               reply_markup=markup)

                logger.info(f" Scraping ({name}) Finished")

            return wrapper

        return decorator

    @print_function_start("Supercategories", dir_name='main_items')
    def main_items_scrapper(self, directory):
        unique_id = 1
        site_main_items = {}
        for super_cat in items_type:

            bot.send_message(self.chat_id, f"🟢 Start scraping in supercategory : {super_cat}")
            bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')
            logger.warning(f"Start scraping in supercategory : {super_cat}")

            url = by_brand_url + super_cat
            soup = self.browser.get_soup(url)
            categories = soup.select("li.producers-item a")
            if len(categories) > 0:
                for category in categories:
                    category_name = category.find('span', class_='producers-text').text.replace("A to Z of ",
                                                                                                "").lower()
                    category_img_tag = category.find('img', class_='producers-img')

                    category_link = baseurl + category['href']
                    cat_img_link = baseurl + category_img_tag['src']
                    cat_img_alt = category_img_tag['alt']

                    site_main_items[unique_id] = {
                        'supercategory': super_cat,
                        'category': category_name,
                        'link': category_link,
                        'category_img_link': cat_img_link,
                        'category_img_alt': cat_img_alt,
                    }

                    self.link_button.text = f'{category_name.capitalize()} Link'
                    self.link_button.url = category_link
                    new_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                    new_markup.add(self.link_button)
                    bot.send_photo(
                        self.chat_id, photo=cat_img_link,
                        caption=f"SuperCategory:  {super_cat}\nCategory:  {category_name}",
                        reply_markup=new_markup)
                    bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')

                    logger.warning(f"Category ({category_name}) is Saved.")
                    unique_id += 1
            else:
                logger.error("Request Failed Because of Human Verification")
                bot.send_message(self.chat_id, "🔴Human Verification Failed")

        # region : Saving
        now_time = get_time()
        full_path = directory + f'{now_time}' + f'({unique_id - 1}).csv'
        csv_main_items_saver(site_main_items, full_path)
        bot.send_document(self.chat_id, open(full_path, 'r'), caption=f"Report of MainItems Scrapping at ({now_time})")
        if os.path.isfile(directory + f'main_items.csv'):
            os.remove(directory + f'main_items.csv')
        os.rename(full_path, directory + f'main_items.csv')
        # endregion : Saving

    @print_function_start("AllOffers", dir_name='all_offers')
    def all_offers_scrapper(self, directory):
        saved_products = {}
        unique_id = 1
        i = 1

        while 1:

            bot.send_message(self.chat_id, f"🟢 Page ({i})")
            bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')

            logger.warning(f"Page ({i})")
            soup = self.browser.get_soup(all_offers_url.format(i))
            # region : pagination numbers
            try:
                end_number = int(soup.find("span", class_='paging-count__value js-paging-count__value--end').text)
                total_number = int(soup.find("span", class_='paging-count__value js-paging-count__value--total').text)
                # endregion : pagination numbers

                products_list = soup.find_all("li", class_="product-grid__item")
                for item in products_list:
                    saved_products[unique_id] = product_scrapper(self.browser, item)
                    if saved_products[unique_id] is not None:
                        # region:Telegram notify

                        self.link_button.text = f'More Info'
                        self.link_button.url = saved_products[unique_id]['product_details']['link']

                        new_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                        new_markup.add(self.link_button)
                        bot.send_photo(
                            self.chat_id,
                            photo=saved_products[unique_id]['product_details']['image_detail']['image_link'],
                            caption=f"Title:  {saved_products[unique_id]['product_title']}\n"f"Brand:  {saved_products[unique_id]['product_details']['brand']}\n"f"Rating:  {saved_products[unique_id]['product_details']['rating']} /5 \n"f"Percentages:  {saved_products[unique_id]['product_details']['percentages']}\n"f"Availability:  {saved_products[unique_id]['product_details']['availability']}\n"f"Price:  {saved_products[unique_id]['product_details']['price']}\n"f"Unit Price:  {saved_products[unique_id]['product_details']['unit_price']}\n",
                            reply_markup=new_markup)

                        bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')

                        # endregion:Telegram notify
                        unique_id += 1
                    else:
                        del saved_products[unique_id]

                if end_number == total_number:
                    break

            except AttributeError or IndexError:
                bot.send_message(self.chat_id, "🔴Page Not Found")

            finally:
                i = i + 1

        # region : Saving
        now_time = get_time()
        full_path = directory + f'{now_time}' + f'({unique_id - 1}).csv'
        csv_saver(saved_products, full_path)
        bot.send_document(self.chat_id, open(full_path, 'r'), caption=f"Report of AllOffers Scrapping at ({now_time})")
        if os.path.isfile(directory + f'all_offers.csv'):
            os.remove(directory + f'all_offers.csv')
        os.rename(full_path, directory + f'all_offers.csv')
        # endregion : Saving

    @print_function_start("Brands", dir_name='brands')
    def brands_scrapper(self, directory):
        unique_id = 1
        brands = {}
        file_path = '../csv/main_items/main_items.csv'

        try:
            df = pd.read_csv(file_path)
            scrapped_main_items = df.set_index('id').T.to_dict()

        except Exception as e:
            scrapped_main_items = None

        if scrapped_main_items:
            bot.send_message(self.chat_id, "🟢Start scraping (Brands)")
            for key in scrapped_main_items.keys():
                bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')
                supercategory = scrapped_main_items[key]['supercategory']
                category = scrapped_main_items[key]['category']
                brands_collection_url = scrapped_main_items[key]['link']
                brands_collection_page_soup = self.browser.get_soup(brands_collection_url)
                brand_sections = brands_collection_page_soup.select("a.az-item-link")

                for brand in brand_sections:
                    brand_link = baseurl + brand['href']
                    brand_name = brand.find('span', class_='az-item-name').text

                    try:
                        brand_img_link = baseurl + brand.find('img')['src']
                    except IndexError or AttributeError:
                        brand_img_link = None
                    try:
                        brand_img_alt = brand.find('img')['alt']
                    except IndexError or AttributeError:
                        brand_img_alt = None

                    brands[unique_id] = {
                        'brand_name': brand_name,
                        'supercategory': supercategory,
                        'category': category,
                        'brand_link': brand_link,
                        'brand_img_link': brand_img_link,
                        'brand_img_alt': brand_img_alt,
                    }

                    # region:Telegram notify
                    self.link_button.text = f'Products of {brand_name}'
                    self.link_button.url = brands[unique_id]['brand_link']

                    new_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                    new_markup.add(self.link_button)

                    bot.send_photo(
                        self.chat_id,
                        photo=brands[unique_id]['brand_img_link'],
                        caption=f"Title:  {brands[unique_id]['brand_name']}\nSupercategory:  {brands[unique_id]['supercategory']}\nCategory:  {brands[unique_id]['category']} \n",
                        reply_markup=new_markup)
                    # endregion:Telegram notify

                    logger.warning(f"Brand ({brand_name}) is Saved.")
                    unique_id += 1

            # region : Saving
            now_time = get_time()
            full_path = directory + f'{now_time}' + f'({unique_id - 1}).csv'
            csv_brand_saver(brands, full_path)
            bot.send_document(self.chat_id, open(full_path, 'r'), caption=f"Report of Brands Scrapping at ({now_time})")
            if os.path.isfile(directory + f'brands.csv'):
                os.remove(directory + f'brands.csv')
            os.rename(full_path, directory + f'brands.csv')
            # endregion : Saving

        else:
            bot.send_message(self.chat_id, text="🛑 First you should start scraping (Main Items)")
            logger.error("First you should start scraping (Main items)")

    @print_function_start("NewProducts", dir_name='new_products')
    def new_products_scrapper(self, directory):

        soup = self.browser.get_soup(new_products_url)

        sections = soup.find_all("li", class_="np-postlist__item")
        if len(sections) > 0:

            for section in sections:
                saved_products = {}
                unique_id = 1
                # region: Date Section
                section_date, section_title, section_items_count, section_description = date_section(section)
                bot.send_message(self.chat_id, f"Products in ({section_date})")
                bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')
                # endregion: Date Section

                # region: Products Section
                products_list = section.find_all("li", class_="product-grid__item")
                for item in products_list[:-1]:
                    saved_products[unique_id] = new_product_scrapper(self.browser, item, section_date)
                    if saved_products[unique_id] is not None:

                        # region:Telegram notify
                        self.link_button.text = f'More Info'
                        self.link_button.url = saved_products[unique_id]['product_details']['link']

                        new_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                        new_markup.add(self.link_button)
                        bot.send_photo(
                            self.chat_id,
                            photo=saved_products[unique_id]['product_details']['image_detail']['image_link'],
                            caption=f"Title:  {saved_products[unique_id]['product_title']}\n"f"Brand:  {saved_products[unique_id]['product_details']['brand']}\n"f"Rating:  {saved_products[unique_id]['product_details']['rating']} /5 \n"f"Percentages:  {saved_products[unique_id]['product_details']['percentages']}\n"f"Availability:  {saved_products[unique_id]['product_details']['availability']}\n"f"Price:  {saved_products[unique_id]['product_details']['price']}\n"f"Unit Price:  {saved_products[unique_id]['product_details']['unit_price']}\n",
                            reply_markup=new_markup)
                        bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')

                        # endregion:Telegram notify

                        unique_id += 1
                    else:
                        del saved_products[unique_id]
                # endregion: Products Section

                # region : Saving
                directory = directory_creator(directory + f"{section_date.replace(' ', '')}/")
                now_time = get_time()
                full_path = directory + f'{now_time}' + f'({unique_id}).csv'
                csv_saver(saved_products, full_path)
                bot.send_document(self.chat_id, open(full_path, 'r'),
                                  caption=f"Report of NewProducts Scrapping at ({section_date})")
                if os.path.isfile(directory + f'new_products.csv'):
                    os.remove(directory + f'new_products.csv')
                os.rename(full_path, directory + f'new_products.csv')
                # endregion : Saving


        else:
            bot.send_message(self.chat_id, "Page Not Found")

    @print_function_start("ProductsbyBrands", dir_name='products_by_brands')
    def products_by_brand_scrapper(self, directory):
        file_path = '../csv/brands/brands.csv'
        try:
            df = pd.read_csv(file_path)
            scrapped_brands = df.set_index('id').T.to_dict()
            for key in list(scrapped_brands.keys())[:2]:
                brand_name = scrapped_brands[key]['brand_name']
                directory = directory_creator(directory + brand_name + '/')
                saved_products = {}
                i = 1
                unique_id = 1
                while 1:
                    logger.info(f"Page ({i}) of Brand ({brand_name})")
                    bot.send_message(self.chat_id, f"Page ({i}) of Brand ({brand_name})")
                    bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')

                    brand_page_link = scrapped_brands[key]['brand_link'] + '?psize=120' + '&pg={}'
                    soup = self.browser.get_soup(brand_page_link.format(i))

                    try:
                        end_number = int(
                            soup.find("span", class_='paging-count__value js-paging-count__value--end').text)
                        total_number = int(
                            soup.find("span", class_='paging-count__value js-paging-count__value--total').text)
                        # endregion : pagination numbers

                        products_list = soup.find_all("li", class_="product-grid__item")
                        for item in products_list:
                            saved_products[unique_id] = product_scrapper(self.browser, item)
                            if saved_products[unique_id] is not None:
                                # region:Telegram notify

                                self.link_button.text = f'More Info'
                                self.link_button.url = saved_products[unique_id]['product_details']['link']

                                new_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                                new_markup.add(self.link_button)
                                bot.send_photo(
                                    self.chat_id,
                                    photo=saved_products[unique_id]['product_details']['image_detail']['image_link'],
                                    caption=f"Title:  {saved_products[unique_id]['product_title']}\n"f"Brand:  {saved_products[unique_id]['product_details']['brand']}\n"f"Rating:  {saved_products[unique_id]['product_details']['rating']} /5 \n"f"Percentages:  {saved_products[unique_id]['product_details']['percentages']}\n"f"Availability:  {saved_products[unique_id]['product_details']['availability']}\n"f"Price:  {saved_products[unique_id]['product_details']['price']}\n"f"Unit Price:  {saved_products[unique_id]['product_details']['unit_price']}\n",
                                    reply_markup=new_markup)

                                bot.send_message(self.chat_id, 'Bot is Working .... be patient 🙏')

                                # endregion:Telegram notify
                                unique_id += 1
                            else:
                                del saved_products[unique_id]

                        if end_number == total_number:
                            break

                    except AttributeError or IndexError:
                        bot.send_message(self.chat_id, "🔴Page Not Found")
                        logger.error("Page Not Found")

                    finally:
                        i = i + 1

                # region : Saving
                now_time = get_time()
                full_path = directory + f'{now_time}' + f'({unique_id - 1}).csv'
                csv_saver(saved_products, full_path)
                bot.send_document(self.chat_id, open(full_path, 'r'),
                                  caption=f"Report of ProductsByBrands Scrapping for brand ({brand_name}) at ({now_time})")
                if os.path.isfile(directory + f'{brand_name}_products.csv'):
                    os.remove(directory + f'{brand_name}_products.csv')
                os.rename(full_path, directory + f'{brand_name}_products.csv')
                # endregion : Saving


        except Exception as e:
            scrapped_brands = None
            bot.send_message(self.chat_id, text="🛑 First you should start scraping (Brands)")
            logger.error("First you should start scraping (Brands)")

    def logo_scrapper(self):
        self.browser.driver.get('https://www.thewhiskyexchange.com/')
        soup = BeautifulSoup(self.browser.driver.page_source, 'html.parser')
        img_link = soup.find_all('img', class_='twe-banner__image twe-banner__image--large')
        link = random.choice(img_link)
        tele_scrapper.welcome_logo = baseurl + link.get('src')
        bot.send_photo(tele_scrapper.chat_id,
                       photo=tele_scrapper.welcome_logo,
                       caption="🔎 Welcome to Scraper Manager of Site (Thewhisky Exchange)",
                       reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    timer_thread = None
    if call.data == "supertypes":
        timer_thread = threading.Thread(target=tele_scrapper.main_items_scrapper, )

    elif call.data == "offers":
        timer_thread = threading.Thread(target=tele_scrapper.all_offers_scrapper, )

    elif call.data == "brands":
        timer_thread = threading.Thread(target=tele_scrapper.brands_scrapper, )

    elif call.data == "newproducts":
        timer_thread = threading.Thread(target=tele_scrapper.new_products_scrapper, )

    elif call.data == "productsbybrand":
        timer_thread = threading.Thread(target=tele_scrapper.products_by_brand_scrapper, )

    timer_thread.start()
    timer_thread.join()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Bot is Working .... be patient 🙏')
    tele_scrapper.chat_id = message.chat.id
    tele_scrapper.browser = Browser()
    tele_scrapper.logo_scrapper()


def start_bot():
    bot.polling()


if __name__ == '__main__':
    tele_scrapper = TelegramScrapper()
    logger.info("Please send /Start command in bot")
    bot_thread = threading.Thread(target=start_bot, )
    bot_thread.start()
