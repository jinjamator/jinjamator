from jinjamator.external.celery.backends.database.models import Task as DB_Job, JobLog
from sqlalchemy import create_engine, select, delete, and_, or_, exc
from sqlalchemy.orm import Session
from datetime import date
from datetime import timedelta

if keep_for_days <= 0:
    log.info(f"Log cleanup for severities {','.join(log_severities_to_delete)} disabled")

select_older_than = date.today() - timedelta(days=keep_for_days)


engine=create_engine(self._configuration["celery_result_backend"])
global_count=0
job_count=0

with Session(engine) as session:
    try:
        rs = session.execute(
            select(
                [
                    DB_Job.id,
                    DB_Job.task_id,
                    DB_Job.status,
                    DB_Job.date_done,
                    DB_Job.date_start,
                    DB_Job.date_scheduled,
                    DB_Job.jinjamator_task,
                    DB_Job.created_by_user_id,
                ]
            ).where(DB_Job.date_done < select_older_than).order_by(DB_Job.id.asc())
        )
    except exc.SQLAlchemyError as e:
        log.error(e)
        return None
    
    for job in rs.fetchall():
        job_count+=1
        # log.debug(f"compressing logs for task {job.task_id}")
        conditions = [JobLog.level == sev for sev in log_severities_to_delete]

        try:
            rs = session.execute(
                delete(JobLog).where(and_(JobLog.task_id == job.task_id,or_(*conditions)))
            )
        except exc.SQLAlchemyError as e:
            log.error(e)
            return None
        session.commit()
        global_count+=rs.rowcount
        # log.debug(f"removed {rs.rowcount} logs of severities: {','.join(log_severities_to_delete)}")

log.info(f"removed {global_count} logs in  of severities: {','.join(log_severities_to_delete)}")
