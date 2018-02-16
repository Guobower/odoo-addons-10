# -*- coding: utf-8 -*-
{
    'name': "Enterprise theme branding",

    'summary': """
        Color and Background cutomisation for any company""",

    'description': """
        Change color theme, app switcher background and footer logo.
    """,

    'author': "odoo@e-cosi.com",
    'website': "http://www.e-cosi.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'web',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['web_enterprise', 'web'],

    # always loaded
    'data': [
        'views/assets_backend.xml'
    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],

    'installable': True,
}
