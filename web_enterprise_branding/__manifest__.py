# -*- coding: utf-8 -*-
{
    'name': "SCAM branding",

    'summary': """
        Color and Background cutosmisation for SCAM Company""",

    'description': """
        Change color theme, app switcher background and footer logo.
    """,

    'author': "odoo@e-cosi.com",
    'website': "http://www.e-cosi.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'web',
    'version': '1.0.0',

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
