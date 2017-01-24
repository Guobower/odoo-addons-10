# -*- coding: utf-8 -*-
{
    'name': "Data Exchange",

    'summary': """
        Manage and operate import and export streams""",

    'description': """
        Manage and operate import and export streams.

        Streams use adapters to acquire or output data in native format. Datas
        are stored in an intermediate model permitting to follow treatments and
        retry failures.

        Adapters could be provide by inheritance et package using odoo modules.

        Suggestions & Feedback to: lionel.deglise@e-cosi.com""",

    'author': "lionel.deglise@e-cosi.com",
    'website': "http://www.e-cosi.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Exchange',
    'version': '1.2.0',
    'licence': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/dataexchange_views.xml',
    ],

    'installable': True,
    'application': True,
}
