from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

if not self._configuration["celery_result_backend"].startswith("sqlite"):
    log.info("Result backend not SQLite")
    return None

log.info(f'doing vaccum on {self._configuration["celery_result_backend"]}')

engine=create_engine(self._configuration["celery_result_backend"])

with engine.connect() as conn:
    with conn.execution_options(isolation_level='AUTOCOMMIT'):
        conn.execute(text("vacuum"))


