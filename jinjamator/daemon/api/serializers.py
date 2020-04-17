from flask_restx import fields
from jinjamator.daemon.api.restx import api


site = api.model('site',{
        'id': fields.String(required=True, description='Generated ID of site'),
        'name': fields.String(required=True, description='Generated name of site'),
    }
)


environment = api.model('environment',{
        'id': fields.String(required=True, description='Generated ID of environment'),
        'name': fields.String(required=True, description='Name of environment'),
        'path': fields.String(required=True, description='Path to environment'),
        'sites': fields.List(fields.Nested(site))
    }
)

environments =  api.model(
    'List of environments', { 'environments':fields.List(fields.Nested(environment)) }
)

task_info = api.model('task_info',{
        'id': fields.String(required=True, description='Generated ID of task'),
        'path': fields.String(required=True, description='Relative task path to base_dir'),
        'base_dir': fields.String(required=True, description='Basedir where task was found'),
        'description': fields.String(required=True, description='Description of task'),

}
)

tasks =  api.model(
    'List of tasks', { 'tasks':fields.List(fields.Nested(task_info)) }
)
