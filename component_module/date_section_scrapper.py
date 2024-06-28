from python_utils.logger import logger


def date_section(section_soup):
    date = ""
    date_section = section_soup.select("div.np-posthead div.np-posthead__meta p span")
    if len(date_section) > 0:
        for item in date_section:
            date = date + item.text
        date = date.replace("\n", " ")
    else:
        date = "No Date"

    title = section_soup.select_one("div.np-posthead div.np-posthead__info h2").text.strip()
    items_count = section_soup.select_one("div.np-posthead div.np-posthead__info p").text.strip()
    description = section_soup.select_one("div.np-posthead div.np-posthead__info div").text.strip()

    logger.info('***************************')
    logger.info(f'Date:{date}')
    logger.info(f'Title:{title}')
    logger.info(f'Items:{items_count}')
    logger.info(f'Description:{description}')
    logger.info('***************************')

    return date, title, items_count, description
