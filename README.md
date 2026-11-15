# Equipment Maintenance

Módulo de Odoo (18.0) para la gestión del mantenimiento de equipos: planificación de
mantenimientos, seguimiento de sus tareas y control de horas, con flujos de estado
automáticos y vistas Kanban/Lista/Formulario para el trabajo diario.

## ¿De qué trata el módulo?

El módulo gira en torno a tres modelos:

| Modelo | Descripción |
|---|---|
| `equipment.maintenance.equipment` | Catálogo de equipos (activos) a los que se les da mantenimiento. |
| `equipment.maintenance.maintenance` | Una intervención de mantenimiento sobre un equipo (cabecera), compuesta por una o varias tareas. |
| `equipment.maintenance.task` | Cada tarea concreta dentro de un mantenimiento (quién la ejecuta, cuándo, cuántas horas tomó). |

Un **Equipo** puede tener muchos **Mantenimientos**, y cada **Mantenimiento** se
descompone en una o varias **Tareas**. El estado y las horas del mantenimiento se
calculan automáticamente a partir del estado y las horas de sus tareas.

## Funcionalidades principales

### Equipos (`equipment.maintenance.equipment`)
- Datos básicos: nombre, código y ubicación.

### Mantenimientos (`equipment.maintenance.maintenance`)
- **Numeración automática**: cada mantenimiento recibe una secuencia única al
  crearse (`ir.sequence`, formato `MNT/<año>/#####`).
- **Planificación por fechas**: `date_start` / `date_end` y las *Horas Planificadas*
  (`planned_hours`) se calculan automáticamente como la diferencia entre ambas
  fechas. No se permite que la fecha fin sea anterior a la de inicio.
- **Horas ejecutadas** (`hours`): suma automática de las horas reportadas en todas
  sus tareas.
- **Responsables** (`responsible_ids`): se calculan a partir de los responsables de
  las tareas asociadas.
- **Estado derivado automáticamente** (`state`) de sus tareas, sin que el usuario
  lo edite manualmente:
  - Sin tareas → `Draft` (Borrador).
  - Todas sus tareas canceladas → `Cancelled` (Cancelado).
  - Al menos una tarea completada con horas reportadas, y el resto completadas o
    canceladas → `Done` (Completado).
  - Cualquier tarea en ejecución o completada (sin cumplir lo anterior) →
    `In Progress` (En ejecución). Es decir, en cuanto una tarea pasa a ejecución,
    el mantenimiento pasa a ejecución.
  - En cualquier otro caso → `Draft`.
- **Acción "Cancelar"**: es la única transición manual disponible sobre el
  mantenimiento; cancela todas sus tareas (incluidas las ya completadas), lo que
  deja el mantenimiento en estado `Cancelled`. No se puede cancelar si ya está
  cancelado o si no tiene tareas.
- **Acceso directo a sus tareas** desde la vista Kanban (botón con el contador de
  tareas).

### Tareas (`equipment.maintenance.task`)
- Datos: nombre, mantenimiento al que pertenece, equipo (relacionado desde el
  mantenimiento), fecha, horas, descripción y responsable.
- **Flujo de estado** con botones validados (no siempre visibles, solo en el
  estado que corresponde):
  - **Iniciar** (`action_start`): solo desde `Draft` → `In Progress`.
  - **Completar** (`action_done`): solo desde `In Progress` → `Done`. **Exige que
    se hayan reportado horas (> 0)** antes de poder completarse.
  - **Cancelar** (`action_cancel`): permitido desde `Draft` o `In Progress`;
    bloqueado si la tarea ya está `Done` o `Cancelled`.
- **Las horas nunca pueden ser negativas** (restricción en el modelo), tanto en
  tareas como, por extensión, en los totales calculados del mantenimiento.

### Vistas Kanban
- **Tareas**: agrupadas por estado, con barra de progreso, borde de color e
  insignia según el estado, horas y avatar del responsable.
- **Mantenimientos**: agrupadas por estado, mostrando secuencia, nombre, equipo,
  responsable de creación, horas ejecutadas y un acceso directo a sus tareas.

## Seguridad y permisos

Se definen dos grupos de seguridad (categoría *Equipment Maintenance*):

| Grupo | Descripción |
|---|---|
| **User** (`group_equipment_maintenance_user`) | Personal de mantenimiento: gestiona mantenimientos y tareas del día a día. |
| **Manager** (`group_equipment_maintenance_manager`) | Incluye al grupo User (`implied_ids`) y además administra el catálogo de equipos. |

Permisos (`ir.model.access.csv`):

| Modelo | User | Manager |
|---|---|---|
| Equipos | Solo lectura | Lectura, escritura, creación, eliminación |
| Mantenimientos | Lectura, escritura, creación (sin eliminar) | Lectura, escritura, creación, eliminación |
| Tareas | Lectura, escritura, creación (sin eliminar) | Lectura, escritura, creación, eliminación |

El menú **Configuración → Equipos** solo es visible para el grupo *Manager*; el
resto del menú raíz (**Mantenimientos**, **Tareas**) requiere pertenecer al grupo
*User* (o *Manager*, que lo incluye).

## Estructura del módulo

```
equipment_maintenance/
├── data/                    # Secuencia de mantenimientos (ir.sequence)
├── models/                  # equipment, maintenance, task
├── security/                # Grupos y ir.model.access.csv
├── static/src/scss/         # Estilos de las vistas Kanban
├── tests/                   # Pruebas automatizadas (TransactionCase)
└── views/                   # Vistas (list/kanban/form/search) y menús
```

## Tests

El módulo incluye pruebas automatizadas en `tests/test_equipment_maintenance.py`
(`TransactionCase`):

1. **`test_maintenance_sequence_is_assigned_on_create`**: verifica que cada
   mantenimiento recibe una secuencia única al crearse.
2. **`test_task_state_workflow_validations`**: verifica el flujo de estado de una
   tarea (no se puede completar sin iniciarla, no se puede iniciar dos veces, no
   se puede completar sin horas reportadas, no se puede cancelar una tarea ya
   completada).
3. **`test_maintenance_state_follows_tasks_and_blocks_negative_hours`**: verifica
   que el estado del mantenimiento se deriva correctamente del de sus tareas, y
   que no se permiten horas negativas.

Para ejecutarlas:

```bash
odoo-bin -c odoo.conf -d <base_de_datos> -i equipment_maintenance --test-enable --stop-after-init
```
