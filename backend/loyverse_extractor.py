"""
Driver to extract information out of Loyverse and send to staging phase
"""
import json

from .drivers.loyapi import get_categories_all, get_items_all
from .utils.redis import get_redis_connection, flush_data, add_to_redis
from .utils.vars import PROCESSED_DATA_PREFIX, RAW_DATA_PREFIX
from .utils.loyverse import extract_catids, merge_items_categories, extract_variant_information


def extract_loyverse_data(save_raw=False, flush_redis=True, debug=False):
    """
    Main pipeline

    :param save_raw: Whether to save raw unfiltered data from Loyverse to Redis or not
    :param flush_redis: Flush redis database before adding latest information
    :param debug: Boolean to print stuff on console for debugging
    """
    all_items = get_items_all(debug=debug)
    category_ids = extract_catids(all_items)
    all_categories = get_categories_all(category_ids, debug=debug)
    all_products = merge_items_categories(all_items, all_categories, debug=debug)
    all_products_variants = extract_variant_information(all_products, debug=debug)

    # Add data to redis
    if flush_redis:
        flush_data()

    # Add variant data
    add_to_redis(all_products_variants, 'SKU', PROCESSED_DATA_PREFIX)

    # Add raw data if directed
    if save_raw:
        add_to_redis(all_products, 'id', RAW_DATA_PREFIX)


if __name__ == '__main__':
    extract_loyverse_data(save_raw=False, flush_redis=True, debug=True)
