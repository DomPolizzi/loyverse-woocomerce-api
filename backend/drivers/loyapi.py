import requests

from backend.utils import LOYVERSE_API_BASE, LOYVERSE_ALL_ITEMS_ENDPOINT, LOYVERSE_ALL_CATEGORIES_ENDPOINT, Loytoken
from backend.utils.loyverse import determine_cursor


def get_items_all(debug=False):
    """
    Function to get all items (make recurring calls) from Loyverse database

    :param debug: Boolean to print stuff on console for debugging
    :returns: list of dicts containing information about every item in Loyverse system
    """
    get_items_url = LOYVERSE_API_BASE + LOYVERSE_ALL_ITEMS_ENDPOINT
    headers = {
        'Authorization': Loytoken,
    }

    # First call
    params = {
        'limit': 250
    }
    response = requests.get(get_items_url, params=params, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
    else:
        response_json = None
        if debug:
            print("Error encountered: {}".format(response.text))
        exit()

    # Variable to store all items in...
    all_items = response_json['items']

    # Check if more results are needed
    cursor = determine_cursor(response_json)

    # Iterate until the last batch of items received
    pages = 1
    while cursor:
        params['cursor'] = cursor
        response = requests.get(get_items_url, params=params, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            if debug:
                print("{} pages recieved.".format(pages))
                pages += 1
        elif response.status_code == 429:
            if debug:
                print("Rerunning page: {}.".format(pages))
            continue
        else:
            response_json = None
            # TODO: Decision: Try again, add logic based on error, or stop iteration but still use the items that are
            #  received in previous iterations
            if debug:
                print("Error encountered: {}".format(response.text))
            exit()

        all_items = all_items + response_json['items']
        cursor = determine_cursor(response_json)

    return all_items


def get_categories_all(categories, debug=False):
    """
    Function to get all categories specified by the arguments from Loyverse

    :param categories: list of category ids
    :param debug: Boolean to print stuff on console for debugging
    :return: dict containing dicts of categories with their id as key
    """
    # Comma-separated string containing all the categories of interest we need
    categories_ids = ','.join(categories)

    get_categories_url = LOYVERSE_API_BASE + LOYVERSE_ALL_CATEGORIES_ENDPOINT
    headers = {
        'Authorization': Loytoken,
    }

    # First call
    params = {
        'limit': 250,
        'categories_ids': categories_ids
    }
    response = requests.get(get_categories_url, params=params, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
    else:
        response_json = None
        if debug:
            print("Error encountered: {}".format(response.text))
        exit()

    # Variable to store all items in...
    all_categories = response_json['categories']

    # Check if more results are needed
    cursor = determine_cursor(response_json)

    # Iterate until the last batch of items received
    pages = 1
    while cursor:
        params['cursor'] = cursor
        response = requests.get(get_categories_url, params=params, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            if debug:
                print("{} pages recieved.".format(pages))
                pages += 1
        elif response.status_code == 429:
            if debug:
                print("Rerunning page: {}.".format(pages))
            continue
        else:
            response_json = None
            # TODO: Decision: Try again, add logic based on error, or stop iteration but still use the items that are
            #  received in previous iterations
            if debug:
                print("Error encountered: {}".format(response.text))
            exit()

        all_categories = all_categories + response_json['categories']
        cursor = determine_cursor(response_json)

    all_categories_dict = dict()
    for category in all_categories:
        all_categories_dict[category['id']] = category

    return all_categories_dict
