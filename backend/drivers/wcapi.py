"""
Driver to make changes to WooCommerce System using the API
"""
import json
from backend.utils import (WOOCOMMERCE_ATTRIBUTES_ENDPOINT, WOOCOMMERCE_ATTRIBUTE_TERMS_ENDPOINT_F,
                           WOOCOMMERCE_CATEGORIES_ENDPOINT, WOOCOMMERCE_PRODUCTS_ENDPOINT,
                           WOOCOMMERCE_PRODUCT_VARIATIONS_ENDPOINT_F, wcapi)


def get_attribute(att_id):
    """
    Function to get attribute information using the provided id.

    :param att_id: ID of the Attribute to get.
    :return: dictionary containing attribute information or None if attribute was not found
    """
    response = wcapi.get("{}/{}".format(WOOCOMMERCE_ATTRIBUTES_ENDPOINT, att_id))
    if response.status_code == 404:
        return None
    return response.json()


def get_attributes_all():
    """
    Function to get all attributes.

    :return: list of dicts containing attribute information
    """
    params = {'context': 'edit'}
    response = wcapi.get(WOOCOMMERCE_ATTRIBUTES_ENDPOINT, params=params)
    if response.status_code != 200:
        return None

    return response.json()


def post_attribute(name, slug, att_type='select', order_by='menu_order', has_archives=True):
    """
    Function to create an attribute in WooCommerce System.
    Attributes are unique on slug in WooCommerce System

    :param name: Name of the attribute
    :param slug: Slug of the attribute
    :param att_type: Type of the attribute. Default: 'select'
    :param order_by: How to order in the menu. Default: 'menu_order'
    :param has_archives: Attribute has archives or not. Default: 'True'

    :return: dictionary containing attribute information
    """
    data = {
        "name": name,
        "slug": slug,
        "type": att_type,
        "order_by": order_by,
        "has_archives": has_archives
    }

    response = wcapi.post(WOOCOMMERCE_ATTRIBUTES_ENDPOINT, data)

    # If the attribute was not found, search for the Attribute with this slug
    if response.status_code == 400 and response.json()['code'] == 'woocommerce_rest_cannot_create':
        response_json = get_attributes_all()

        # WooCommerce recognizes 'color' and 'pa_color' as same slug.
        for item in response_json:
            if item['slug'] == slug or item['slug'] == 'pa_{}'.format(slug):
                return item
    else:
        return response.json()


def get_attribute_term(attribute_id, term_id):
    """
    Function to get attribute term information using the provided id.

    :param attribute_id: ID of the Attribute
    :param term_id: ID of the term to get
    :return: dictionary containing attribute term information or None if attribute was not found
    """
    response = wcapi.get("{}/{}".format(WOOCOMMERCE_ATTRIBUTE_TERMS_ENDPOINT_F.format(attribute_id), term_id))
    if response.status_code == 404:
        return None
    return response.json()


def post_attribute_term(attribute_id, name, slug, html_description=None, menu_order=None):
    """
    Function to create an attribute term in WooCommerce System.
    Attribute terms are unique on name in WooCommerce System

    :param attribute_id: ID of parent attribute
    :param name: Name of the attribute term
    :param slug: Slug of the attribute term
    :param html_description: HTML description for the attribute term
    :param menu_order: Order in Menu for this term

    :return: dictionary containing attribute term information
    """
    data = {
        "name": name,
        "slug": slug,
    }
    if html_description:
        data['description'] = html_description
    if menu_order:
        data['menu_order']: menu_order

    response = wcapi.post(WOOCOMMERCE_ATTRIBUTE_TERMS_ENDPOINT_F.format(attribute_id), data)

    # If the attribute was not found, search for the Attribute with this slug
    if response.status_code == 400 and response.json()['code'] == 'term_exists':
        response_json = response.json()
        return get_attribute_term(attribute_id, response_json['data']['resource_id'])
    else:
        return response.json()


def get_category(cat_id):
    """
    Function to get category information based on id.

    :param cat_id: ID of the Attribute
    :return: dictionary containing category information or None if attribute was not found
    """
    response = wcapi.get('{}/{}'.format(WOOCOMMERCE_CATEGORIES_ENDPOINT, cat_id))
    if response.status_code == 404:
        return None
    return response.json()


def post_category(name, slug, parent_id=None, html_description=None, display=None, menu_order=None):
    """
    Function to create an attribute term in WooCommerce System.
    Attribute terms are unique on name in WooCommerce System

    :param name: Name of the attribute term
    :param slug: Slug of the attribute term
    :param parent_id: Id of the parent resource
    :param html_description: HTML description for the attribute term
    :param display: Category archive display type. Options: 'default', 'products', 'subcategories' and 'both'
    :param menu_order: Order in Menu for this category

    :return: dictionary containing attribute term information
    """
    data = {
        "name": name,
        "slug": slug,
    }
    if parent_id:
        data['parent'] = parent_id
    if html_description:
        data['description'] = html_description
    if display:
        data['display'] = display
    if menu_order:
        data['menu_order']: menu_order

    response = wcapi.post(WOOCOMMERCE_CATEGORIES_ENDPOINT, data)
    # If the attribute was not found, search for the Attribute with this slug
    if response.status_code == 400 and response.json()['code'] == 'term_exists':
        response_json = response.json()
        return get_category(response_json['data']['resource_id'])
    else:
        return response.json()


def get_product(product_id):
    """
    Function to get product based on it's id.

    :param product_id: ID of the product
    :return: Dict containing information of the product or None if the product wasn't found
    """
    response = wcapi.get('{}/{}'.format(WOOCOMMERCE_PRODUCTS_ENDPOINT, product_id))
    if response.status_code == 404:
        return None
    return response.json()


def search_product(slug):
    """
    Function to search for a product using it's slug

    :param slug: Slug to use for searching the product
    :return: dictionary containing information of the product or None if product wasn't found
    """
    params = {
        'slug': slug
    }
    response = wcapi.get(WOOCOMMERCE_PRODUCTS_ENDPOINT, params=params)
    if len(response.json()) > 0:
        return response.json()[0]
    else:
        return None


def post_product(product_name, slug, product_type, status='publish', description=None, short_description=None,
                 sku: str = None, regular_price: str = None, manage_stock=True, stock_quantity=None, weight: str = None,
                 image_urls=None, dimensions=None, category_id=None, tags_ids=None, attribute_id=None,
                 attribute_options=None, attribute_variation=None, attribute_visible=True, attribute_term_name=None,
                 default_attributes=None, menu_order=None):
    """
    Function to create a product in WooCommerce System.

    Notes
    =====
    - Dev Decided on this: Creating a variable product without a SKU will duplicate the product. So, we need to use the slug to search for
        that product manually before sending POST.
    - OR Another Option: Set a SKU for the variable product as well. How do we generate this SKU such that it can be replicated
            across multiple reruns needs to be decided.

    :param product_name: Name of the product
    :param slug: Slug of the product
    :param product_type: Type (Main ones are 'simple' and 'variable'
    :param status: Status of the product. Options: 'draft', 'pending', 'private' and 'publish'
    :param description: Description of the product
    :param short_description: Short description of the product
    :param sku: SKU of the product. Must Str type
    :param regular_price: Price of the product. Must Str type
    :param manage_stock: Whether to manage stock for this product or not
    :param stock_quantity: Quantity of the product in stock
    :param weight: Weight of the product. Must Str type
    :param image_urls: List of image urls to for the product
    :param dimensions: Dimensions of the product. A dict object with 'length', 'width', and 'height' information
    :param category_id: Category ID of the product. Will be processed into a category object for WooCommerce API
    :param tags_ids: Tag ids of the product. Will be processed into a Tag array object for WooCommerce API
    :param attribute_id: ONLY FOR VARIABLE PRODUCT - Attribute id of the Product Variation. Will be processed into an
                Attribute object for WooCommerce API
    :param attribute_options: List of term names for the product's attribute based on which the variants exist
    :param attribute_variation: Boolean whether the attribute terms names are used to change product variations
    :param attribute_visible: Boolean whether the attribute and it's options are visible in the product page
    :param attribute_term_name: ONLY FOR VARIABLE PRODUCT - Attribute term name of the Product Variation. Will be
                processed into an Attribute object for WooCommerce API
    :param default_attributes: Default Attributes of the product. Will be processed into a Default Attributes array
                object for WooCommerce API. A list of dict objects with 'id', 'name', and 'option' information
    :param menu_order: Menu order of the product. To Custom sort the product
    :return: a tuple with a boolean of whether the product already exists and a dictionary containing information
                of the product
    """
    # Check if exists
    product_exists = search_product(slug)
    if product_exists:
        return True, product_exists

    # Create new
    data = {
        'name': product_name,
        'slug': slug,
        'type': product_type,
    }
    if status:
        data['status'] = status
    if description:
        data['description'] = description
    if short_description:
        data['short_description'] = short_description
    if sku:
        data['sku'] = sku
    if regular_price:
        data['regular_price'] = regular_price
    if manage_stock is not None:
        data['manage_stock'] = manage_stock
    if stock_quantity:
        data['stock_quantity'] = stock_quantity
    if weight:
        data['weight'] = weight
    if dimensions:
        data['dimensions'] = dimensions
    if category_id:
        data['categories'] = [{'id': category_id}]
    if tags_ids:
        tags_list = list()
        [tags_list.append({'id': tag_id}) for tag_id in tags_ids]
        data['tags'] = tags_list

    # Attributes are a bit tricky
    # A product can have an attribute-option combo
    # Or it can be a variable product with attributes and a list of options for variations
    if attribute_id and attribute_term_name and not attribute_options:
        # Case when a product has a single attribute-option combo
        data['attributes'] = [
            {
                'id': attribute_id,
                'option': attribute_term_name
            }
        ]
    elif attribute_id and attribute_options and attribute_variation is not None:
        # Case when it's a variable product and has a bunch of options for a single attribute
        data['attributes'] = [
            {
                'id': attribute_id,
                'options': attribute_options,
                'variation': attribute_variation,
                'visible': attribute_visible
            }
        ]
        # In this case, we define default attribute as the first option in our list
        data['default_attributes'] = [
            {
                'id': attribute_id,
                'option': attribute_options[0]
            }
        ]

    # Or someone can edit the code and custom-define the default attribute
    if default_attributes:
        data['default_attributes'] = default_attributes
    if menu_order:
        data['menu_order'] = menu_order

    # Add urls of images to the POST data
    if image_urls:
        if len(image_urls) != 0:
            counter = 0
            image_dicts = list()
            for image_url in image_urls:
                counter += 1
                image_dicts.append(
                    {
                        # WE NEED TO FORCE A FILETYPE IN THE IMAGE URL OR WOOCOMMERCE WON'T ACCEPT IT
                        'src': '{}.png'.format(image_url),
                        'name': "{} Image {}".format(product_name, counter),
                        'alt': product_name
                    }
                )
            data['images'] = image_dicts

    response = wcapi.post(WOOCOMMERCE_PRODUCTS_ENDPOINT, data)
    if response.status_code == 400 and response.json()['code'] == 'product_invalid_sku':
        response_json = response.json()
        if 'resource_id' in response_json['data']:
            return True, get_product(response_json['data']['resource_id'])
        else:
            return None, response_json
    else:
        return False, response.json()


def get_product_variation(product_id, variation_id):
    """
    Function to get product variation information.

    :param product_id: Product ID of the parent product
    :param variation_id: Variation ID to get
    :return: dict containing information of the variation or None if not found
    """
    response = wcapi.get('{}\{}'.format(WOOCOMMERCE_PRODUCT_VARIATIONS_ENDPOINT_F.format(product_id), variation_id))
    if response.status_code == 404:
        return None
    return response.json()


def post_product_variation(product_name, product_id, sku: str, regular_price: str = None, status='publish',
                           description=None, manage_stock=True, stock_quantity=None, weight: str = None,
                           image_urls=None, dimensions=None, attribute_id=None, attribute_term_name=None,
                           menu_order=None):
    """
    Function to create a product variations in WooCommerce System.
    # TODO: Add image to the POST

    :param product_name: Name of the parent product
    :param product_id: Id of the parent product
    :param sku: SKU of the product. Must Str type
    :param regular_price: Price of the product. Must Str type
    :param status: Status of the product. Options: 'draft', 'pending', 'private' and 'publish'
    :param description: Description of the product
    :param manage_stock: Whether to manage stock for this product or not
    :param stock_quantity: Quantity of the product in stock
    :param weight: Weight of the product. Must Str type
        :param image_urls: List of image urls to for the product

    :param dimensions: Dimensions of the product. A dict object with 'length', 'width', and 'height' information
    :param attribute_id: ONLY FOR VARIABLE PRODUCT - Attribute id of the Product Variation. Will be processed into an
                Attribute object for WooCommerce API
    :param attribute_term_name: ONLY FOR VARIABLE PRODUCT - Attribute term name of the Product Variation. Will be
                processed into an Attribute object for WooCommerce API
    :param menu_order: Menu order of the product. To Custom sort the product
    :return: a tuple with a boolean of whether the product already exists and a dictionary containing information
                of the product
    """
    # Create new
    data = {
        'sku': str(sku)
    }
    if status:
        data['status'] = status
    if description:
        data['description'] = description
    if regular_price:
        data['regular_price'] = str(regular_price)
    if manage_stock is not None:
        data['manage_stock'] = manage_stock
    if stock_quantity:
        data['stock_quantity'] = stock_quantity
    if weight:
        data['weight'] = str(weight)
    if dimensions:
        data['dimensions'] = dimensions
    if attribute_id and attribute_term_name:
        data['attributes'] = [
            {
                'id': attribute_id,
                'option': attribute_term_name
            }
        ]
    if menu_order:
        data['menu_order'] = menu_order

    # Add urls of images to the POST data
    if image_urls:
        if len(image_urls) != 0:
            counter = 0
            image_dicts = list()
            for image_url in image_urls:
                counter += 1
                image_dicts.append(
                    {
                        # WE NEED TO FORCE A FILETYPE IN THE IMAGE URL OR WOOCOMMERCE WON'T ACCEPT IT
                        'src': '{}.png'.format(image_url),
                        'name': "{} Image {}".format(product_name, counter),
                        'alt': product_name
                    }
                )
            data['images'] = image_dicts

    response = wcapi.post(WOOCOMMERCE_PRODUCT_VARIATIONS_ENDPOINT_F.format(product_id), data)
    if response.status_code == 400 and response.json()['code'] == 'product_invalid_sku':
        response_json = response.json()
        if 'resource_id' in response_json['data']:
            return True, get_product(response_json['data']['resource_id'])
        else:
            return None, response_json
    else:
        return False, response.json()
