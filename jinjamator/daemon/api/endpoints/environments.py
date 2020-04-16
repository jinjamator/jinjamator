import logging

from flask import request
from flask_restx import Resource
from jinjamator.daemon.api.serializers import environments
from jinjamator.daemon.api.restx import api
from flask import current_app as app
import glob
import os
import xxhash

log = logging.getLogger()

ns = api.namespace('environments', description='Operations related to jinjamator environments')

@ns.route('/')
class EnvironmentCollection(Resource):
    @api.marshal_with(environments)
    def get(self):
        """
        Returns the list of discoverd environments found in global_environments_base_dirs.
        """

        response = { 'environments': [] }
        for env_base_dir in app.config["JINJAMATOR_ENVIRONMENTS_BASE_DIRECTORIES"]:
            for env_dir in glob.glob( os.path.join(env_base_dir,'*') ):
                
                if os.path.isdir(env_dir):
                    environment_name = os.path.basename(env_dir)
                    current_environment = {
                        'id': xxhash.xxh64(environment_name).hexdigest(),
                        "path": env_dir,
                        "name": environment_name,
                        "sites": []
                    }
                    for site_dir in glob.glob(os.path.join(env_base_dir,environment_name,'sites','*')):
                        if os.path.isdir(site_dir):
                            site_name = os.path.basename(site_dir)
                            site = {
                                'id': xxhash.xxh64(site_name).hexdigest(),
                                'name': site_name
                            }
                            current_environment['sites'].append(site)
            response['environments'].append(current_environment)

        return response