e-COSI addons for Odoo (formerly OpenERP)
========================

This repository contains a collection of Odoo modules.

# Modules

| Module | Odoo Version | Description |
| --- | --- | --- |
| **dataexchange** | 10.0 | base module to manage file import/export with logging et retry on fail features. Extensibility based on abstract adapters |
| **web_enterprise_branding** | 10.0 | module to change backend  theme elements for custom branding, it applies for Enterprise version |

## web_enterprise_branding

This module is a template. To be used it must be cloned and datas updated for specific environnement.

Elements to override :

For easy use, images must be replaced with the same name.

| Element | Path | Effect |
| --- | --- | --- |
| App switch footer logo | static/src/img/logo_footer.png | The logo in the footer of application switcher |
| App switcher background | static/src/img/brand-bg.jpg | Background image for applications switcher |
| App switcher caption style | static/src/lass/web_branding.less | div.o_caption.o_caption_brand
| Colors, fonts and other | static/src/lass/variables.less | You can override any var of default theme in this file |

Note : it could be used to customize a specific environnement eg: testing of everything else !

# Requirements

* Odoo 10.0
