# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class EquipmentMaintenanceEquipment(models.Model):
    _name = 'equipment.maintenance.equipment'
    _description = 'EquipmentMaintenanceEquipment'

    name = fields.Char('Name')
    code = fields.Char('Code', unique=True)
    location = fields.Char('Location')
