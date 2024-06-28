import pandas as pd

from python_utils.get_time import get_time
from python_utils.logger import logger


def product_data_normalizer(data):
    processed_data = []
    for key, value in data.items():
        row = {
            'id': key,
            'title': value['product_title'],
            'brand': value['product_details']['brand'],
            'category': value['product_details']['category'],
            'link': value['product_details']['link'],
            'image_link': value['product_details']['image_detail']['image_link'],
            'image_alt': value['product_details']['image_detail']['image_alt'],
            'rating': value['product_details']['rating'],
            'percentages': value['product_details']['percentages'],
            'price': value['product_details']['price'],
            'unit_price': value['product_details']['unit_price'],
            'availability': value['product_details']['availability'],
            'description': value['product_details']['description'],
            'style': value['product_details']['style'],
            'characters': value['product_details']['characters'],
            'facts': value['product_details']['facts']
        }
        processed_data.append(row)
    return processed_data


def brand_data_normalizer(data):
    processed_data = []
    for key, value in data.items():
        row = {
            'id': key,
            'brand_name': value['brand_name'],
            'supercategory': value['supercategory'],
            'category': value['category'],
            'brand_link': value['brand_link'],
            'brand_img_link': value['brand_img_link'],
            'brand_img_alt': value['brand_img_alt'],
        }
        processed_data.append(row)
    return processed_data


def main_item_data_normalizer(data):
    processed_data = []
    for key, value in data.items():
        row = {
            'id': key,
            'supercategory': value['supercategory'],
            'category': value['category'],
            'link': value['link'],
        }
        processed_data.append(row)
    return processed_data


def csv_saver(data, path):
    pre_processed_data = product_data_normalizer(data)
    df = pd.DataFrame(pre_processed_data)
    df.to_csv(path, index=False)
    logger.warning(f"Item's File saved to {path}")


def csv_main_items_saver(data, path):
    pre_processed_data = main_item_data_normalizer(data)
    df = pd.DataFrame(pre_processed_data)
    df.to_csv(path, index=False)
    logger.warning(f"Item's File Saved To {path}")


def csv_brand_saver(data, path):
    pre_processed_data = brand_data_normalizer(data)
    df = pd.DataFrame(pre_processed_data)
    df.to_csv(path, index=False)
    logger.warning(f"Item's File saved to {path}")
