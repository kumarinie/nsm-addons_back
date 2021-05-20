# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Magnus Red BV (http://www.magnus.nl)
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from openerp import models, fields, api, _


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = 'account.payment.line.create'

    # Overridden:
    @api.multi
    def _prepare_move_line_domain(self):
        domain = super(AccountPaymentLineCreate, self)._prepare_move_line_domain()
        index = domain.index(('invoice_id.state', '=', 'verified'))
        domain = domain[:index]
        domain += [('invoice_id.state', 'in', ['verified','verified_by_publisher']),
                   '&', ('invoice_id.state', '=', 'auth'), '&',
                   ('invoice_id.verif_tresh_exceeded', '=', False),
                   ('invoice_id.verif_tresh_exceeded_2', '=', False)]
        return domain
