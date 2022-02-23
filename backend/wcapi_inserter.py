"""
Script uses wcapi.py to access WooCommerce and insert product information to the WooCommerce system
"""

from .utils import PROCESSED_DATA_PREFIX, get_milli_time, SLUG_PREFIXES
from .utils.woocommerce import generate_slug
from .drivers.wcapi import post_attribute, post_attribute_term, post_category, \
    post_product, post_product_variation
from .utils.redis import get_all_items


def insert_to_woocommerce(debug=False):
    """
    Main pipeline

    Steps:
    ======
    1. Retrieve the list of products to upload
    2. Get a list of categories to create from products list
    3. Process them into their two different types, single products and variables
    4. For each product, based on their type, decide attributes, and attribute terms to create
    5. Create attributes, attribute terms, and categories through POST
    6. Insert single products and parent products for variants through POST
    7. Insert variants for variable products through POST
    """
    product_list = get_all_items(prefix=PROCESSED_DATA_PREFIX, as_list=True)
    categories_dict = get_all_categories(product_list)
    single_products, variable_products = determine_product_types(product_list)
    attributes_dict = determine_attributes(variable_products)

    start_time = get_milli_time()
    categories_dict = create_categories(categories_dict, debug=debug)
    attributes_dict = create_attributes(attributes_dict, debug=debug)
    single_products = create_single_products(single_products, categories_dict, debug=debug)
    variable_products = create_variable_products(variable_products, categories_dict, attributes_dict, debug=debug)
    variable_products = create_variants(variable_products, attributes_dict, debug=debug)
    end_time = get_milli_time() - start_time
    print('Total Time Taken: {}ms ({}s)'.format(end_time, end_time / 1000))


def get_all_categories(product_list):
    """
    Function to get a unique list of categories out of the list of products.

    :param product_list: List of products
    :return: dict with category names as keys
    """
    categories_dict = dict()
    for product in product_list:
        if product['category_name'] not in categories_dict and product['category_name']:
            categories_dict[product['category_name']] = None

    return categories_dict


def determine_product_types(product_list):
    """
    Function to go through a list of products and define their types.
    Two or more products with the same handle/name are variants of a variable product.

    :param product_list: List of products containing both types of products
    :return: tuple with a dict containing single products and a dict containing lists of variable products
    """
    handle_count = dict()
    for product in product_list:
        if product['handle'] not in handle_count:
            handle_count[product['handle']] = {'count': 1}
        else:
            handle_count[product['handle']]['count'] += 1

    # Handles with count greater than one are variable products
    for handle in handle_count:
        if handle_count[handle]['count'] == 1:
            handle_count[handle]['type'] = 'single'
        else:
            handle_count[handle]['type'] = 'variable'

    # Compile dicts
    # All dicts because it will be easier to append more information to products later
    single_products = dict()
    variable_products = dict()
    for product in product_list:
        if handle_count[product['handle']]['type'] == 'single':
            single_products[product['handle']] = product
        else:
            # Some data duplication here but these are local dictionaries. Not sure if it's worth it to clean them
            if product['handle'] in variable_products:
                variable_products[product['handle']]['variants'].append(product)
            else:
                variable_products[product['handle']] = {'variants': [product]}

    return single_products, variable_products


def determine_attributes(variable_products):
    """
    Function to go through all the products and get a list of attributes and attribute terms. Single products do not
    have any attributes.

    :param variable_products: Dict containing list of variations of variable products
    :return: dict of attributes and their terms
    """

    # This is a complex dictionary.
    #   - The parent element keys are names of attributes
    #   - The parent elements contain a 'terms' dictionary that has keys as the attribute term and it's value is the
    #       attribute_term id coming from WooCommerce
    #   - The parent elements will also be added with an id entry when the attribute is created in WooCommerce
    attributes = dict()
    for handle in variable_products:
        variable_product = variable_products[handle]
        for variation in variable_product['variants']:
            # These NoneType will be filled with WooCommerce Attribute Term IDs later
            if variation['option_1_name'] not in attributes:
                attributes[variation['option_1_name']] = {'terms': {variation['option_1_value']: None}}
            else:
                attributes[variation['option_1_name']]['terms'][variation['option_1_value']] = None

    return attributes


def create_categories(categories_dict, debug=False):
    """
    Function to create categories in WooCommerce.

    :param categories_dict: Dict to get category names from
    :param debug: Boolean to print stuff on console for debugging
    :returns: the same categories dict with ids assigned to the category names
    """
    for category in categories_dict:
        slug = generate_slug(category, 'category')
        wc_category = post_category(category, slug)
        categories_dict[category] = wc_category['id']
        if debug:
            print('Created/Retrieved category: {}'.format(category))

    return categories_dict


def create_attributes(attributes_dict, debug=False):
    """
    Function to create attributes and attribute terms in WooCommerce System.

    :param attributes_dict: Dict containing attributes and their terms
    :param debug: Boolean to print stuff on console for debugging
    :return: the same dict with ids of attributes and terms added
    """
    for attribute in attributes_dict:
        attribute_slug = generate_slug(attribute, 'attribute')
        wc_attribute = post_attribute(attribute, attribute_slug)
        attributes_dict[attribute]['wc_id'] = wc_attribute['id']
        if debug:
            print('Created/Retrieved attribute: {}'.format(attribute))

        # Use attribute id to create terms for that attribute as well
        for term in attributes_dict[attribute]['terms']:
            term_slug = generate_slug(term, 'attribute_term')
            wc_attribute_term = post_attribute_term(attributes_dict[attribute]['wc_id'], term, term_slug)
            attributes_dict[attribute]['terms'][term] = wc_attribute_term['id']
            if debug:
                print('\tCreated/Retrieved attribute term: {}'.format(term))
    return attributes_dict


def create_single_products(single_products, categories_dict, debug=False):
    """
    Function to create single products in WooCommerce System.

    :param single_products: Dict containing dicts of information for single products
    :param categories_dict: Dict containing category names and their WooCommerce id
    :param debug: Boolean to print stuff on console for debugging
    :return: the same dict with ids of products added
    """
    for handle in single_products:
        product = single_products[handle]
        if not product['category_name']:
            category_id = None
        else:
            category_id = categories_dict[product['category_name']]

        slug = '{}{}'.format(SLUG_PREFIXES['product'], handle)
        if 'image_url' in product and product['image_url']:
            image_urls = [product['image_url']]
        else:
            image_urls = None
        already_exists, wc_product = post_product(product['name'], slug, 'simple', sku=product['SKU'],
                                                  category_id=category_id, regular_price=str(product['price']),
                                                  manage_stock=False, image_urls=image_urls)
        single_products[handle]['wc_id'] = wc_product['id']
        if debug and already_exists is not None:
            print("Created Product: {}. Already Existed: {}".format(handle, already_exists))
        elif debug and already_exists is None:
            print("Could not create product: {}. Error: {}".format(handle, wc_product))

        # if already_exists:
        # TODO: Perhaps update the product information if it already exists?
        #   Definitely need to do so for quantity

    return single_products


def create_variable_products(variable_products, categories_dict, attributes_dict, debug=False):
    """
    Function to create variable products in WooCommerce System.

    :param variable_products: Dict containing dicts of information for variable products
    :param categories_dict: Dict containing category names and their WooCommerce id
    :param attributes_dict: Dict containing information about attributes
    :param debug: Boolean to print stuff on console for debugging
    :return: the same dict with ids of products added
    """
    for handle in variable_products:
        product = variable_products[handle]['variants'][0]
        variant_attribute_name = variable_products[handle]['variants'][0]['option_1_name']
        variant_attribute_id = attributes_dict[variant_attribute_name]['wc_id']
        variant_attribute_term_names = get_attribute_terms(variable_products[handle])
        if not product['category_name']:
            category_id = None
        else:
            category_id = categories_dict[product['category_name']]

        slug = '{}{}'.format(SLUG_PREFIXES['product'], handle)
        if 'image_url' in product and product['image_url']:
            image_urls = [product['image_url']]
        else:
            image_urls = None
        already_exists, wc_product = post_product(product['name'], slug, 'variable', category_id=category_id,
                                                  manage_stock=False, image_urls=image_urls,
                                                  attribute_id=variant_attribute_id,
                                                  attribute_options=variant_attribute_term_names,
                                                  attribute_variation=True, attribute_visible=True)
        variable_products[handle]['wc_id'] = wc_product['id']
        if debug:
            print("Created Product: {}. Already Existed: {}".format(handle, already_exists))

        # if already_exists:
        # TODO: Perhaps update the product information if it already exists?
        #   Definitely need to do so for quantityvariable_products

    return variable_products


def get_attribute_terms(product):
    """
    Function to iterate through all variants of a variable product and compile a list of attribute terms from them.

    :param product: Variable product and variants information
    :return: list of term names
    """
    attribute_terms = list()
    for variation in product['variants']:
        if variation['option_1_value'] not in attribute_terms:
            attribute_terms.append(variation['option_1_value'])
    return attribute_terms


def create_variants(variable_products, attributes_dict, debug=False):
    """
    Function to create variations for variable products in WooCommerce System.

    :param variable_products: Dict containing dicts of information for variable products
    :param attributes_dict: Dictionary containing information of attributes
    :param debug: Boolean to print stuff on console for debugging
    :return: the same dict with ids of products added
    """
    for handle in variable_products:
        if 'image_url' in variable_products[handle] and variable_products[handle]['image_url']:
            image_urls = [variable_products[handle]['image_url']]
        else:
            image_urls = None

        for variant in variable_products[handle]['variants']:
            already_exists, wc_product_variant = post_product_variation(variant['name'],
                                                                        variable_products[handle]['wc_id'],
                                                                        variant['SKU'], variant['price'],
                                                                        image_urls=image_urls,
                                                                        attribute_id=attributes_dict[
                                                                            variant['option_1_name']]['wc_id'],
                                                                        attribute_term_name=variant['option_1_value'],
                                                                        manage_stock=False)
            variant['wc_id'] = wc_product_variant['id']
            if debug:
                print("Created Product variation: {}. Already Existed: {}".format(handle, already_exists))

        # if already_exists:
        # TODO: Perhaps update the product information if it already exists?
        #   Definitely need to do so for quantityvariable_products

    return variable_products


if __name__ == '__main__':
    insert_to_woocommerce(debug=True)
