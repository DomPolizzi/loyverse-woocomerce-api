import re

from backend.utils import SLUG_PREFIXES


def generate_slug(category, entity_type):
    """
    Function to use the category name and create a slug from it.
    TODO: We can use a library to slugify our strings but it needs to be a very strictly regulated system because they
        are the only way of keeping things from being duplicated. In case a library updates and changes how they create
        slugs, it could cause a serious problem of duplication in WooCommerce.

    :param category: Category name
    :param entity_type: Type of entity to get prefix
    :return: slug string
    """
    prefix = SLUG_PREFIXES[entity_type]

    slug = category.lower()
    slug = re.sub('[^a-zA-B ]', '', slug)
    slug = re.sub('\\s+-\\s+', '-', slug)
    slug = re.sub('\\s+', '-', slug)

    slug = '{}{}'.format(prefix, slug)

    return slug
