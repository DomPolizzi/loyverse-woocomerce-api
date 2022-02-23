"""
Test to get a list of items form LoyVerse API.
Very crude, very rough code to complete it quickly.
"""
import requests
from utils.vars import LOYVERSE_API_BASE, LOYVERSE_ALL_ITEMS_ENDPOINT
from auth.auth import Loytoken


def main():
    url = LOYVERSE_API_BASE + LOYVERSE_ALL_ITEMS_ENDPOINT
    headers = {
        'Authorization': Loytoken,
    }
    params = {
        'limit': 250
    }
    # request = requests.get(url, headers=headers)
    request = requests.get(url, params=params, headers=headers)
    print(request.text)

    # print(request.text)
    # print(request.status_code)


if __name__ == '__main__':
    main()
