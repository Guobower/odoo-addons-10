# -*- coding: utf-8 -*-
{
    'name': "e-COSI Help Menu",

    'summary': """Add a help link in the user menu to a choosen URL""",

    'description': """
        This module adds a link into the top right menu (user menu), named "Online Help".
        You can choose in the Settings app the URL linked to this menu.
    """,

    'author': "e-COSI",
    'website': "http://www.e-cosi.com",

    'category': 'Administration',

    'version': '1.O',

    'depends': ['base'],

    'data': [
        'views/assets.xml',
        'views/general_configuration.xml',
        'data/actions.xml',
    ],

    'qweb': [
        'static/src/xml/base.xml',
    ],
}