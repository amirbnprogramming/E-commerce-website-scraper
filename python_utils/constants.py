import telebot

baseurl = "https://www.thewhiskyexchange.com"

products_url = baseurl + '/c/35/japanese-whisky?pg={}'
products_csv = '../csv/products'

new_products_path = '../csv/new_products/'
new_products_url = baseurl + '/new-products'

all_offers_url = baseurl + '/specialoffers?pg={}&psize=120'
all_offers_path = 'csv/all_offers/'

by_brand_url = baseurl + '/brands/'
items_type = ['worldwhisky', 'champagne-and-wine', 'spirits', 'scotchwhisky']
main_items_path = 'csv/main_items/'

brands_path = 'csv/brands/'
products_brands_path = 'csv/products_by_brands/'

# region :Bot Settings
API_TOKEN = ''

supertypes_button = telebot.types.InlineKeyboardButton('Scrape Super Types', callback_data='supertypes')
offers_button = telebot.types.InlineKeyboardButton('Scrape All Offers', callback_data='offers')
newproducts_button = telebot.types.InlineKeyboardButton('Scrape New Products', callback_data='newproducts')
brands_button = telebot.types.InlineKeyboardButton('Scrape Brands', callback_data='brands')
products_by_brands_button = telebot.types.InlineKeyboardButton('Scrape Products By Brands',
                                                               callback_data='productsbybrand')

markup = telebot.types.InlineKeyboardMarkup(row_width=1)
markup.add(supertypes_button, offers_button, newproducts_button, brands_button, products_by_brands_button)
# endregion :Bot Settings
