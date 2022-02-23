def extract_catids(all_items):
    """
    Function to extract category ids from a list of items

    :param all_items: list of dicts containing item information
    :return: list of categories
    """
    category_ids = list()
    for item in all_items:
        if 'category_id' in item:
            if item['category_id'] not in category_ids and item['category_id']:
                category_ids.append(item['category_id'])

    return category_ids


def determine_cursor(response):
    """
    Function to determine whether a response ahs a cursor or not

    :param response: Response of the URL as a json object
    :return: Nonetype or the Cursor String if cursor was present in the response
    """
    if 'cursor' in response:
        cursor = response['cursor']
    else:
        cursor = None

    return cursor


def merge_items_categories(items, categories, debug=False):
    """
    Function to merge categories into dicts of items to finalize the date in a single variable.

    :param items: list of dicts containing item information
    :param categories: dict of dicts containing category information
    :param debug: Boolean to print stuff on console for debugging
    :return: List of dicts containing item information including their categories
    """
    for item in items:
        if item['category_id']:
            item['category'] = categories[item['category_id']]
    return items


def extract_variant_information(products, debug=False):
    """
    Function to de-normalize the list of variants for each product as defined in the readme.md

    :param products: List of dicts containing products information along with variants and categories
    :param debug: Boolean to print stuff on console for debugging
    :return: List of dicts containing de-normalized variant information including their categories
    """
    all_variants = list()
    for product in products:
        for variant in product['variants']:
            p_handle = product['handle']
            p_SKU = variant['sku']
            p_name = product['item_name']
            if 'category' in product:
                p_category_name = product['category']['name']
                p_category_color = product['category']['color']
            else:
                p_category_name = None
                p_category_color = None
            p_option_1_name = product['option1_name']
            p_option_1_value = variant['option1_value']
            p_price = variant['cost']
            p_main_image_url = product['image_url']
            all_variants.append(
                {
                    'handle': p_handle,
                    'SKU': p_SKU,
                    'name': p_name,
                    'category_name': p_category_name,
                    'category_color': p_category_color,
                    'option_1_name': p_option_1_name,
                    'option_1_value': p_option_1_value,
                    'price': p_price,
                    'image_url': p_main_image_url
                }
            )
    return all_variants
