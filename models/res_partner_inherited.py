# -*- coding: utf-8 -*-
# 1 : imports of python lib

# 2 :  imports of odoo
from odoo import fields, models

# 3 :  imports of odoo modules

# 4 :  imports from custom modules


class ResPartnerInheritedSkype(models.Model):
    """ TODO: добавить описание модели """
    # Private attributes
    # ------------------------------------------------------------------------------------------------------------------

    _inherit = 'res.partner'
    _description = 'Partner Form Inherited for Skype Field'

    # Default methods
    # ------------------------------------------------------------------------------------------------------------------

    # Fields declaration
    # ------------------------------------------------------------------------------------------------------------------

    skype = fields.Char(
        string='Skype',
        size=128,
    )
