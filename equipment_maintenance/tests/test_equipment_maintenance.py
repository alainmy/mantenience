# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestEquipmentMaintenance(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env['equipment.maintenance.equipment'].create({
            'name': 'Compressor 1',
            'code': 'EQ-001',
            'location': 'Plant A',
        })

    def test_maintenance_sequence_is_assigned_on_create(self):
        """A new maintenance gets a unique sequence number from ir.sequence."""
        maintenance = self.env['equipment.maintenance.maintenance'].create({
            'name': 'Preventive Maintenance',
            'equipment_id': self.equipment.id,
        })
        self.assertNotEqual(maintenance.sequence, 'New')
        self.assertTrue(maintenance.sequence)

        maintenance_2 = self.env['equipment.maintenance.maintenance'].create({
            'name': 'Corrective Maintenance',
            'equipment_id': self.equipment.id,
        })
        self.assertNotEqual(maintenance.sequence, maintenance_2.sequence)

    def test_task_state_workflow_validations(self):
        """Tasks can only move through valid states and need hours to be completed."""
        maintenance = self.env['equipment.maintenance.maintenance'].create({
            'name': 'Scheduled Maintenance',
            'equipment_id': self.equipment.id,
        })
        task = self.env['equipment.maintenance.task'].create({
            'name': 'Check oil level',
            'maintenance_id': maintenance.id,
        })

        # A draft task cannot be completed directly.
        with self.assertRaises(UserError):
            task.action_done()

        task.action_start()
        self.assertEqual(task.state, 'in_progress')

        # A task already in progress cannot be started again.
        with self.assertRaises(UserError):
            task.action_start()

        # Completing a task requires reported hours.
        with self.assertRaises(UserError):
            task.action_done()

        task.hours = 1.5
        task.action_done()
        self.assertEqual(task.state, 'done')

        # A completed task can no longer be cancelled.
        with self.assertRaises(UserError):
            task.action_cancel()

    def test_maintenance_state_follows_tasks_and_blocks_negative_hours(self):
        """The maintenance status is derived from its tasks, and hours cannot be negative."""
        maintenance = self.env['equipment.maintenance.maintenance'].create({
            'name': 'Overhaul',
            'equipment_id': self.equipment.id,
        })
        self.assertEqual(maintenance.state, 'draft')

        task = self.env['equipment.maintenance.task'].create({
            'name': 'Replace filter',
            'maintenance_id': maintenance.id,
        })
        task.action_start()
        self.assertEqual(maintenance.state, 'in_progress')

        task.hours = 2
        task.action_done()
        self.assertEqual(maintenance.state, 'done')

        with self.assertRaises(ValidationError):
            task.write({'hours': -1})
