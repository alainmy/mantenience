# -*- coding: utf-8 -*-
{
    'name': 'Equipment maintenance',
    'version': '1.0.0',
    'summary': """ Module for managing equipment maintenance """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    'data': [
        'security/equipment_maintenance_security.xml',
        'security/ir.model.access.csv',
        'data/equipment_maintenance_maintenance_sequence.xml',
        'views/equipment_maintenance_equipment_views.xml',
        'views/equipment_maintenance_maintenance_views.xml',
        'views/equipment_maintenance_task_views.xml',
        'views/equipment_maintenance_menus.xml',
    ],
    # 'assets': {
    #           'web.assets_backend': [
    #               'equipment_maintenance/static/src/**/*'
    #           ],
    #       },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
