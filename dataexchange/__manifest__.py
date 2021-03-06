# -*- coding: utf-8 -*-
{
    'name': "Data Exchange",

    'summary': """
        Manage and operate import and export streams""",

    'description': """
***********************
Manage and operate import and export streams.
***********************

Summary
=======
Streams use adapters to acquire or output data in native format. Datas
are stored in an intermediate model permitting to follow treatments and
retry failures.

Adapters could be provide by inheritance et package using odoo modules.

Suggestions & Feedback to: lionel.deglise@e-cosi.com

Changelog
=========
v11.0.1.3.1
-----------
- [IMP] Add {{db_name}} param in webhook url and payload

v11.0.1.3.0
-----------
- [IMP] Updated to 11.0, nothing to do except metas

v10.0.1.3.0
-----------
- [IMP] Last run execution with state (line is colored too ) and date directly from stream tree
- [IMP] Webhook on run success and failure (ex: heartbeat.io, or Slack notification)

v10.0.1.2.1
-----------
- [FIX] Retry now updates run state
- [IMP] Export retry is no more TODO ! It exports in a new file, already extracted record, no new extraction

""",

    'author': "odoo@e-cosi.com",
    'website': "http://www.e-cosi.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Exchange',
    'version': '11.0.1.3.0',
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
