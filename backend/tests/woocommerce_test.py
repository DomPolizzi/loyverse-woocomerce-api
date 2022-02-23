"""
Test to get a list of items form LoyVerse API.
Very crude, very rough code to complete it quickly.
"""
import requests
from backend.auth.auth import Dev_wcapi as wcapi


def main():
    response = wcapi.get('products/categories/444')
    print(response.text)

if __name__ == '__main__':
    main()
