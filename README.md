# APwhy

Python API that connects Loyverse and Woocomerce

## Requirements:

You will then need to install your Dependencies from requirements.txt

```
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

Redis Docker file

```
docker-compose up
```

Pull Items From Loyverse:

```
    Handle
    SKU
    Name
    Category
    Option 1
    -- Option 1 name
    Option 1 value
    Price
    Photos
```

Push Products to Woocomerce:

```
    Products
    Product Variations
    Product Attributes
    Product Categories
    Product Tags
```

Data being moved need the following:
SKU to match on both sides Name needs to match on both sides Inventory checked and matches Stock in Loyverse

Bonus tasks/Future Plans:    
Little human interaction if possible.  
API will proably run in a cloud as a function or serverless trigger

### Dev Notes:

1. #### Changing Dev configuration to production
   1. Open backend/utils/vars.py
   2. Set ``wcapi`` variable to ``wcapi_prod``
   3. Set ``Loytoken`` variable to ``Loytoken_prod``

### Resources

Loyverse API: https://developer.loyverse.com

Woocomerce API: https://woocommerce.github.io/woocommerce-rest-api-docs

Redis: https://redis.io/