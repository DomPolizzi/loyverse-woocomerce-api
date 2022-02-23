import json

from backend.utils import REDIS_HOST, REDIS_PORT
import redis


def get_redis_connection():
    """
    Function to connect to redis and return a connection
    :return: connection object to redis database
    """
    re_con = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT)
    return re_con


def flush_data():
    """
    Function to clear all data from redis database
    """
    get_redis_connection().flushdb()


def add_to_redis(items, key_name, prefix):
    """
    Function to add data to redis. Takes a list of dictionaries and a key name argument to use as keys.

    :param items: List of dicts
    :param key_name: Key inside of dicts that should be used as redis key
    :param prefix: Prefix the key with this text
    """
    for item in items:
        # Extract key
        if key_name not in item:
            # TODO: Decision, skip this product or crash the whole program?
            print("Error encountered: Defined key name was not found in item dict.")
            exit()
        key = item[key_name]
        if not key:
            # TODO: Decision, skip this product or crash the whole program?
            print("Error encountered: Key cannot be None. Check the data stream.")
            exit()

        recon = get_redis_connection()
        recon.set('{}{}'.format(prefix, key), json.dumps(item))


def get_all_items(prefix=None, to_json=True, decoded_keys=True, as_list=False):
    """
    Function to get all items inside redis based on prefix.

    :param prefix: Look for a pattern at the start of the keys
    :param to_json: Convert values into Json dictionaries instead of sending them as strings
    :param decoded_keys: Decode the keys to strings instead of sending them as binary objects
    :param as_list: Return items as a list of dictionaries instead of a single dictionary with many key-value pairs
    :return: A dict of key-value pairs
    """
    recon = get_redis_connection()

    # Get the full list of keys
    if not prefix:
        encoded_keys = [key for key in recon.keys()]
    else:
        encoded_keys = [key for key in recon.keys() if key.decode().startswith(prefix)]

    # Compile the dictionary
    items_dict = dict()
    for key in encoded_keys:
        value = recon.get(key)

        if not value:
            continue

        if to_json:
            value_to_insert = json.loads(value)
        else:
            value_to_insert = value

        if decoded_keys:
            key_to_insert = key.decode()
        else:
            key_to_insert = key

        items_dict[key_to_insert] = value_to_insert

    # Whether to send the dict or just a list of products
    if as_list:
        return list(items_dict.values())
    else:
        return items_dict
