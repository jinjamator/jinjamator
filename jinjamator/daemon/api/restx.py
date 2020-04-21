import logging
import traceback

from flask_restx import Api

# from rest_api_demo import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

api = Api(
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
