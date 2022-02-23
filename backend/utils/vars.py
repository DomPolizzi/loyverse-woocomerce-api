from backend.auth.auth import, wcapi_prod, Loytoken_dev, Loytoken_prod

# Default Authorizations
wcapi = wcapi_prod
Loytoken = Loytoken_prod

# Loyverse API endpoints
LOYVERSE_API_BASE = 'https://api.loyverse.com/v1.0'
LOYVERSE_ALL_ITEMS_ENDPOINT = '/items'
LOYVERSE_ALL_CATEGORIES_ENDPOINT = '/categories'

# WooCommerce API endpoints
WOOCOMMERCE_ATTRIBUTES_ENDPOINT = 'products/attributes'
WOOCOMMERCE_ATTRIBUTE_TERMS_ENDPOINT_F = 'products/attributes/{}/terms'
WOOCOMMERCE_CATEGORIES_ENDPOINT = 'products/categories'
WOOCOMMERCE_PRODUCTS_ENDPOINT = 'products'
WOOCOMMERCE_PRODUCT_VARIATIONS_ENDPOINT_F = 'products/{}/variations'

# Redis host config
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Redis key prefixes
PROCESSED_DATA_PREFIX = 'final_'
RAW_DATA_PREFIX = 'raw_'

# General
SLUG_PREFIXES = {
    'category': 'wcapi_cat_',
    'attribute': 'wcapi_attribute_',
    'attribute_term': 'wcapi_attribute_term_',
    'product': 'wcapi_prod_',
    'product_variation': 'wcapi_prod_var_',
}
