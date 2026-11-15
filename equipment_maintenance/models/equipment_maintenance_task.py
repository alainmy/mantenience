# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class EquipmentMaintenanceTask(models.Model):
    _name = 'equipment.maintenance.task'
    _description = 'EquipmentMaintenanceTask'

    name = fields.Char('Name')
    maintenance_id = fields.Many2one('equipment.maintenance.maintenance', 'Maintenance')
    equipment_id = fields.Many2one('equipment.maintenance.equipment', 'Equipment',
                                   related='maintenance_id.equipment_id')
    
    date_task = fields.Date(
        string='Day task',
        default=fields.Date.context_today,
    )
    hours = fields.Float('Total Hours')
    description = fields.Text('Description')
    state = fields.Selection(
        [('draft', 'Draft'), 
         ('in_progress', 'In Progress'),
         ('done', 'Done'),
         ('cancelled', 'Cancelled')],
        string='Status',
        default='draft'
    )
    responsible_id = fields.Many2one('res.users', 'Responsible')
    created_by = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.user)
