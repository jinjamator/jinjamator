# Copyright 2019 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from flask import request, g
from flask_restx import Resource
from jinjamator.daemon.api.serializers import environments
from jinjamator.daemon.api.restx import api
from jinjamator.daemon.aaa import require_role
from flask import current_app as app
import glob
import os
import xxhash
from jinjamator.daemon.aaa.models import JinjamatorRole
from jinjamator.daemon.database import db
import copy

log = logging.getLogger()

ns = api.namespace(
    "environments", description="Operations related to jinjamator environments"
)
available_environments = []
preload_defaults_from_site_choices = [""]
site_path_by_name = {}


def discover_environments(app):
    """
    Discovers all environments and sites found in global_environments_base_dirs.
    """

    for env_base_dir in app.config["JINJAMATOR_ENVIRONMENTS_BASE_DIRECTORIES"]:
        for env_dir in glob.glob(os.path.join(env_base_dir, "*")):

            if os.path.isdir(env_dir):
                environment_name = os.path.basename(env_dir)
                current_environment = {
                    "id": xxhash.xxh64(environment_name).hexdigest(),
                    "path": os.path.join(env_base_dir, env_dir),
                    "name": environment_name,
                    "sites": [],
                }
                for site_dir in glob.glob(
                    os.path.join(env_base_dir, environment_name, "sites", "*")
                ):
                    if os.path.isdir(site_dir):
                        site_name = os.path.basename(site_dir)
                        site = {
                            "id": xxhash.xxh64(site_name).hexdigest(),
                            "name": site_name,
                        }
                        current_environment["sites"].append(site)
            available_environments.append(current_environment)
    for env in available_environments:
        env_name = env.get("name")
        for site in env.get("sites"):
            preload_defaults_from_site_choices.append(f"{env_name}/{site.get('name')}")
            site_path_by_name[f"{env_name}/{site.get('name')}"] = os.path.join(
                env.get("path"), "sites", site.get("name")
            )
            dynamic_role_name = f"environment_{env_name}|site_{site.get('name')}"
            new_role = JinjamatorRole(name=dynamic_role_name)
            with app.app_context():
                db.session.add(new_role)
                try:
                    db.session.commit()
                except Exception:
                    pass


@ns.route("/")
class EnvironmentCollection(Resource):
    @require_role(role=None)
    @api.doc(
        params={
            "Authorization": {"in": "header", "description": "A valid access token"}
        }
    )
    @api.marshal_with(environments)
    def get(self):
        """
        Returns the list of discoverd environments found in global_environments_base_dirs.
        """
        user_roles = [role["name"] for role in g._user["roles"]]

        if "administrator" in user_roles or "environments_all" in user_roles:
            response = {"environments": available_environments}
        else:
            user_accessible_environments = []
            for env in copy.deepcopy(available_environments):
                user_accessible_environment_sites = []
                for site in env.get("sites"):
                    if f"environment_{env['name']}|site_{site['name']}" in user_roles:
                        user_accessible_environment_sites.append(site)
                env["sites"] = user_accessible_environment_sites
                if env["sites"]:
                    user_accessible_environments.append(env)
            response = {"environments": user_accessible_environments}

        return response
