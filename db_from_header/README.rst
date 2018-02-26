.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
db_from_header
====================

This addon lets you pass a dbfilter as a HTTP header.

This is interesting for setups where database names can't be mapped to proxied host names eg.
to in a multi-tenant environnement if each client access his backend by subdomain but website
by FQDN.

This module is inspired from the great job of OCA module dbfilter_from_header.

Installation
============

To install this module, you only need to add it to your addons, and load it as
a server-wide module.

This can be done with the ``load`` parameter in ``/etc/odoo.conf`` or with the
``--load`` command-line parameter

``load = "web, web_kanban, db_from_header"``

Configuration
=============

Three headers could by used, select one (only one) of them to choose how filter
is combined with native Odoo dbfilter :
- X-Odoo-dbfilter-only : Odoo dbfilter is not evaluated
- X-Odoo-dbfilter-before : filter is evaluate before Odoo dbfilter (results are passed to Odoo dbfilter)
- X-Odoo-dbfilter-after : filter is evaluate after Odoo dbfilter (it uses Odoo dbfilter results)

If more than one header are set, the first in prevoius order is used.
If none Odoo dbfilter is used.

* For nginx, use:

  ``proxy_set_header X-Odoo-dbfilter-after [your filter regex];``

* For caddy, use:

  ``proxy_header X-Odoo-dbfilter-after [your filter regex]``

* For Apache, use:

  ``RequestHeader set X-Odoo-dbfilter-after [your filter regex]``



Credits
=======

Contributors of intial OCA Module
--------------------------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Holger Brunn <hbrunn@therp.nl>
* Laurent Mignon (aka lmi) <laurent.mignon@acsone.eu>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Fabio Vilchez <fabio.vilchez@clearcorp.co.cr>
* Jos De Graeve <Jos.DeGraeve@apertoso.be>

