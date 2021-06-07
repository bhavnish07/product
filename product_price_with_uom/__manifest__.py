# -*- coding: utf-8 -*-


{
    'name': 'Product_Price_WITH_UOM',
    'version': '1.0.0',
    'sequence': 55,
    'depends': ['base', 'website_sale'],
    'description': "",
    'data': [
        'security/ir.model.access.csv',
        'views/product_price_uom.xml',
        'views/product_detail_page_template.xml',
        'views/assets.xml',
    ],
}
