# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PricelistCategory(models.Model):
    _inherit = 'res.partner.category'
    _name = 'product.pricelist.category'

    parent_id = fields.Many2one('product.pricelist.category')
    child_ids = fields.One2many('product.pricelist.category')
    partner_ids = fields.Boolean(default=False)
    pricelist_ids = fields.Many2many(comodel_name='product.pricelist', string='Pricelists',
        relation='product_pricelist_category_rel',
        column1='category_id', column2='pricelist_id')


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    category_ids = fields.Many2many(comodel_name='product.pricelist.category', string='Pricelist Tags',
        relation='product_pricelist_category_rel',
        column1='pricelist_id', column2='category_id')
