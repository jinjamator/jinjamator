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
import traceback

from flask_restx import Api
from flask import url_for

# from rest_api_demo import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)


class Custom_API(Api):
    @property
    def specs_url(self):
        """
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        """
        return url_for(self.endpoint("specs"), _external=False)


api = Custom_API(
    version="1.0", title="Jinjamator API", description="The REST API of Jinjamator"
)


@api.errorhandler
def default_error_handler(e):
    message = "An unhandled exception occurred."
    log.exception(message)

    # if not settings.FLASK_DEBUG:
    return {"message": message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {"message": "A database result was required but none was found."}, 404
