from odoo import api, fields, models


class PriceUomInfo(models.Model):
    _name = 'price.uom.info'

    uom_id = fields.Many2one(
        'uom.uom', help="uom id of the product.", required=True)
    price = fields.Float(default=0, required=True)

    product_templ_id = fields.Many2one("product.template")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    price_uom_ids = fields.One2many("price.uom.info", "product_templ_id")

    def get_uom_prices(self):
        records = []
        visitor = self.env['website.visitor']._get_visitor_from_request()
        uom_selected = self.env['price.uom.user'].search(
            [('visitor_id', '=', visitor.id), ('product_tmpl_id', '=', self.id)], limit=1)
        for uom in self.price_uom_ids:
            records.append((uom.id, uom.uom_id.id, uom.uom_id.name, uom.price,
                            "selected" if uom.id == uom_selected.uom_id_selected.id else False))

        return records

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist,
                                                                 parent_combination, only_template)
        visitor = self.env['website.visitor']._get_visitor_from_request()
        uom_selected = self.env['price.uom.user'].search(
            [('visitor_id', '=', visitor.id), ('product_tmpl_id', '=', self.id)], limit=1)
        if uom_selected.uom_id_selected:
            res.update({"price": uom_selected.uom_id_selected.price})
        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        values = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        sale_order_line = self.env['sale.order.line'].search([('id', '=', values['line_id'])])
        visitor = self.env['website.visitor']._get_visitor_from_request()
        if sale_order_line:
            uom_selected = self.env['price.uom.user'].search(
                [('visitor_id', '=', visitor.id),
                 ('product_tmpl_id', '=', sale_order_line.product_id.product_tmpl_id.id)], limit=1)
            if uom_selected.uom_id_selected:
                sale_order_line.write({'price_unit': uom_selected.uom_id_selected.price, 'product_uom': uom_selected.uom_id_selected.uom_id.id})
        return values


class PriceUomInfoUser(models.Model):
    _name = "price.uom.user"

    product_tmpl_id = fields.Many2one("product.template", string="Product", required=1, ondelete="cascade")
    uom_id_selected = fields.Many2one("price.uom.info", string="Unit Of Measures", required=1, ondelete="cascade")
    visitor_id = fields.Many2one("website.visitor", string="Visitor", required=1, ondelete="cascade")

    _sql_constraints = [
        # Partial constraint, complemented by a python constraint (see below).
        ('login_key', 'unique (visitor_id, product_tmpl_id)', 'You can not have two users with the same Product!'),
    ]
