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
    date_start = fields.Datetime('Start Date')
    date_end = fields.Datetime('End Date')
    planned_hours = fields.Float('Planned Hours', compute='_compute_planned_hours', store=True)
    hours = fields.Float('Executed Hours', compute='_compute_hours', store=True)
    responsible_ids = fields.One2many('res.users', 'id', 'Responsible',
                                      compute='_compute_responsible_ids')
    task_count = fields.Integer('Task Count', compute='_compute_task_count')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('in_progress', 'In Progress'),
         ('done', 'Done'),
         ('cancelled', 'Cancelled')],
        string='Status',
        compute='_compute_state',
        store=True,
    )
    
    description = fields.Text('Description')
    
    @api.depends('task_ids.responsible_id')
    def _compute_responsible_ids(self):
        for record in self:
            record.responsible_ids = record.task_ids.mapped('responsible_id')

    @api.depends('task_ids.hours')
    def _compute_hours(self):
        for record in self:
            record.hours = sum(task.hours for task in record.task_ids)

    @api.depends('date_start', 'date_end')
    def _compute_planned_hours(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.planned_hours = delta.total_seconds() / 3600.0
            else:
                record.planned_hours = 0.0

    @api.depends('task_ids')
    def _compute_task_count(self):
        for record in self:
            record.task_count = len(record.task_ids)

    @api.depends('task_ids.state', 'task_ids.hours')
    def _compute_state(self):
        for record in self:
            tasks = record.task_ids
            if not tasks:
                record.state = 'draft'
                continue
            if all(task.state == 'cancelled' for task in tasks):
                record.state = 'cancelled'
                continue
            done_tasks = tasks.filtered(lambda t: t.state == 'done')
            other_tasks_closed = all(task.state in ('done', 'cancelled') for task in tasks)
            done_tasks_have_hours = all(task.hours > 0 for task in done_tasks)
            if done_tasks and other_tasks_closed and done_tasks_have_hours:
                record.state = 'done'
            elif any(task.state in ('in_progress', 'done') for task in tasks):
                record.state = 'in_progress'
            else:
                record.state = 'draft'

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and record.date_end < record.date_start:
                raise ValidationError(_('The end date cannot be earlier than the start date.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', 'New') == 'New':
                vals['sequence'] = self.env['ir.sequence'].next_by_code(
                    'equipment.maintenance.maintenance'
                ) or 'New'
        return super().create(vals_list)

    def action_view_tasks(self):
        """Open the tasks of this maintenance, pre-filled for new tasks."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'equipment_maintenance.action_equipment_maintenance_task'
        )
        action['domain'] = [('maintenance_id', '=', self.id)]
        action['context'] = {'default_maintenance_id': self.id}
        action['display_name'] = self.name
        return action

    def action_cancel(self):
        """Cancel the maintenance by cancelling all of its tasks.

        The maintenance has no direct state to write: its status is always
        derived from its tasks, so cancelling it means cancelling them all.
        """
        for record in self:
            if record.state == 'cancelled':
                raise UserError(_('This maintenance is already cancelled.'))
            if not record.task_ids:
                raise UserError(_('There are no tasks to cancel.'))
            record.task_ids.write({'state': 'cancelled'})
