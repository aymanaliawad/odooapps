from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import qrcode
import base64
from io import BytesIO


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    quotation_header = fields.Binary(string="Quotation Header")
    quotation_footer = fields.Binary(string="Quotation Footer")
    invoice_header = fields.Binary(string="Invoice Header")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    warranty = fields.Integer(string="Warranty Duration")
    warranty_type = fields.Selection(
        [
            ("day", "Day(s)"),
            ("week", "Week(s)"),
            ("month", "Month(s)"),
            ("year", "Year(s)"),
        ], required=True, default="day")

    warranty_term = fields.Text("Warranty Term and Conditions")
    delivery_duration = fields.Integer(compute="compute_delivery_duration")

    @api.onchange('commitment_date')
    def compute_delivery_duration(self):
        for rec in self:
            if rec.date_order and rec.commitment_date:
                rec.delivery_duration = (rec.commitment_date - rec.date_order).days
            else:
                rec.delivery_duration = 0


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    qr_code = fields.Binary('QRcode')

    @api.model
    def get_qr_code(self):
        def get_qr_encoding(tag, field):
            company_name_byte_array = field.encode('UTF-8')
            company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
            company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
            return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array

        for record in self:
            qr_code_str = ''
            seller_name_enc = get_qr_encoding(1, record.company_id.display_name)
            company_vat_enc = get_qr_encoding(2, record.company_id.vat or '')
            # date_order = fields.Datetime.from_string(record.create_date)
            time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'), record.create_date)
            timestamp_enc = get_qr_encoding(3, time_sa.isoformat())
            invoice_total_enc = get_qr_encoding(4, str(record.amount_total))
            total_vat_enc = get_qr_encoding(5,
                                            str(record.currency_id.round(record.amount_total - record.amount_untaxed)))

            str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
            qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            return qr_code_str

    @api.model
    def create(self, vals):
        res = super(AccountMoveInherit, self).create(vals)
        return res


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    l10n_ae_vat_amount = fields.Monetary(compute='_compute_vat_amount', string='VAT Amount')

    @api.depends('price_subtotal', 'price_total')
    def _compute_vat_amount(self):
        for record in self:
            record.l10n_ae_vat_amount = record.price_total - record.price_subtotal
