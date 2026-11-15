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
    sequence = fields.Char('Sequence', related='maintenance_id.sequence', store=True, readonly=True)
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

    @api.constrains('hours')
    def _check_hours(self):
        for task in self:
            if task.hours < 0:
                raise ValidationError(_('Hours cannot be negative.'))

    def action_start(self):
        """Put the task in progress. Only allowed from draft."""
        for task in self:
            if task.state != 'draft':
                raise UserError(_('Only draft tasks can be put in progress.'))
            task.state = 'in_progress'

    def action_done(self):
        """Complete the task. Hours worked must be reported first."""
        for task in self:
            if task.state != 'in_progress':
                raise UserError(_('Only tasks in progress can be completed.'))
            if not task.hours:
                raise UserError(_('You must report the hours worked before completing the task.'))
            task.state = 'done'

    def action_cancel(self):
        """Cancel the task. Not allowed once it is already done or cancelled."""
        for task in self:
            if task.state in ('done', 'cancelled'):
                raise UserError(_('Completed or already cancelled tasks cannot be cancelled.'))
            task.state = 'cancelled'
