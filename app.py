from backend.loyverse_extractor import extract_loyverse_data
from backend.wcapi_inserter import insert_to_woocommerce

if __name__ == '__main__':
    extract_loyverse_data(debug=True)
    insert_to_woocommerce(debug=True)
