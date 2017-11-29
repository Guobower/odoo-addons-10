# -*- coding: utf-8 -*-
{
    'name': "e-COSI Catégories pour les listes de prix",

    'summary': """
        Ajoute des étiquettes aux listes de prix avec des sous-catégories""",

    'description': """
    """,

    'author': "odoo@e-cosi.com",
    'website': "http://www.e-cosi.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'views/product_pricelist.xml',
        'views/pricelist_tags_menu.xml',
    ],
}