import logging

from flask import request
from flask_restx import Resource
from jinjamator.daemon.api.serializers import tasks
from jinjamator.daemon.api.restx import api
from jinjamator.tools.docutils_helper import get_section_from_task_doc
from jinjamator.task import JinjamatorTask
from flask import current_app as app
from flask import jsonify
import glob
import os
import xxhash

log = logging.getLogger()

ns = api.namespace('tasks', description='Operations related to jinjamator tasks')

global available_tasks
available_tasks_by_id={}
available_tasks_by_path={}

@ns.route('/')
class TaskList(Resource):
    @api.marshal_with(tasks)
    def get(self):
        """
        Returns the list of discoverd tasks found in global_tasks_base_dirs.
        """
        
        response = { 'tasks': [] }
        added_tasks = []
        for tasks_base_dir in app.config["JINJAMATOR_TASKS_BASE_DIRECTORIES"]:            
            for file_ext in ['py','j2']:
                
                for task_dir in glob.glob( os.path.join(tasks_base_dir,'**',f'*.{file_ext}'), recursive=True):
                    
                    append = True
                    for dir_chunk in os.path.dirname(task_dir.replace(tasks_base_dir,'')).split(os.path.sep): # filter out hidden directories
                        if dir_chunk.startswith(".") or dir_chunk in ['__pycache__']:
                            append = False
                            break
                    
                    if append:
                        dir_name = os.path.dirname(task_dir.replace(tasks_base_dir,''))[1:]
                        task_id = xxhash.xxh64(task_dir).hexdigest()
                        task = {
                                'id':task_id,
                                'path': dir_name,
                                'base_dir': tasks_base_dir,
                                'description': get_section_from_task_doc(task_dir) or 'no description'
                            
                        }
                        if task_id not in added_tasks:                    
                            available_tasks_by_id[task_id]=task
                            available_tasks_by_path[dir_name]=task
                            response['tasks'].append(task)
        
        return response

@ns.route('/<string:id>')
@api.response(404, 'Task not found.')
class Task(Resource):
    def get(self, id):
        """
        Returns details for specified task.

        Use this method to generate a wizard via alpaca.js.
        """

        if len(available_tasks_by_id.keys()) == 0:
            task_list = TaskList()
            task_list.get()

        if not available_tasks_by_id.get(id):
            return None, 404
        
        task_info=available_tasks_by_id[id]
        
        task = JinjamatorTask()
        task.load(os.path.join(task_info['base_dir'],task_info['path']))
        log.info(task.get_jsonform_schema())
        return jsonify(task.get_jsonform_schema())

