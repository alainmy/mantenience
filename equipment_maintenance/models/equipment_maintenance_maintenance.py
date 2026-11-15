# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class EquipmentMaintenanceMaintenance(models.Model):
    _name = 'equipment.maintenance.maintenance'
    _description = 'EquipmentMaintenanceMaintenance'

    name = fields.Char('Name')
    sequence = fields.Char('Sequence', default='New', copy=False, readonly=True)
    created_by = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.user)
    equipment_id = fields.Many2one('equipment.maintenance.equipment', 'Equipment')
    task_ids = fields.One2many('equipment.maintenance.task', 'maintenance_id', 'Tasks')
    hours = fields.Float('Total Hours', compute='_compute_hours', store=True)
    responsible_ids = fields.One2many('res.users', 'id', 'Responsible',
                                      compute='_compute_responsible_ids')
    
    description = fields.Text('Description')
    
    @api.depends('task_ids.responsible_id')
    def _compute_responsible_ids(self):
        for record in self:
            record.responsible_ids = record.task_ids.mapped('responsible_id')

    @api.depends('task_ids.hours')
    def _compute_hours(self):
        for record in self:
            record.hours = sum(task.hours for task in record.task_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', 'New') == 'New':
                vals['sequence'] = self.env['ir.sequence'].next_by_code(
                    'equipment.maintenance.maintenance'
                ) or 'New'
        return super().create(vals_list)
