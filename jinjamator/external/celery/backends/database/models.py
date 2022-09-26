# -*- coding: utf-8 -*-
"""Database models used by the SQLAlchemy result store backend."""
from __future__ import absolute_import, unicode_literals

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.types import PickleType

from celery import states

from .session import ResultModelBase

__all__ = ("Task", "TaskSet", "JobLog")


class Task(ResultModelBase):
    """Task result/status."""

    __tablename__ = "celery_taskmeta"
    __table_args__ = {"sqlite_autoincrement": True}

    id = sa.Column(
        sa.Integer,
        sa.Sequence("task_id_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    task_id = sa.Column(sa.String(155), unique=True, index=True)
    status = sa.Column(sa.String(50), default=states.PENDING)
    result = sa.Column(PickleType, nullable=True)
    date_done = sa.Column(
        sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )
    date_scheduled = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=True)
    date_start = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=True)
    traceback = sa.Column(sa.Text, nullable=True)
    jinjamator_task = sa.Column(sa.String(1024), nullable=False, default="")
    created_by_user_id = sa.Column(sa.Integer, nullable=False)
    debugger_password = sa.Column(sa.Text, nullable=True)

    def __init__(self, task_id):
        self.task_id = task_id

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "result": self.result,
            "traceback": self.traceback,
            "date_done": self.date_done,
            "date_start": self.date_start,
            "date_scheduled": self.date_scheduled,
            "jinjamator_task": self.jinjamator_task,
            "created_by_user_id": self.created_by_user_id,
            "debugger_password": self.debugger_password,
        }

    def __repr__(self):
        return "<Task {0.task_id} for {0.jinjamator_task} state: {0.status}>".format(
            self
        )


class TaskSet(ResultModelBase):
    """TaskSet result."""

    __tablename__ = "celery_tasksetmeta"
    __table_args__ = {"sqlite_autoincrement": True}

    id = sa.Column(
        sa.Integer,
        sa.Sequence("taskset_id_sequence"),
        autoincrement=True,
        primary_key=True,
    )
    taskset_id = sa.Column(sa.String(155), unique=True)
    task_id = sa.Column(sa.String(155))
    result = sa.Column(PickleType, nullable=True)
    date_done = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=True)

    def __init__(self, taskset_id, result):
        self.taskset_id = taskset_id
        self.result = result

    def to_dict(self):
        return {
            "taskset_id": self.taskset_id,
            "result": self.result,
            "date_done": self.date_done,
        }

    def __repr__(self):
        return "<TaskSet: {0.taskset_id}>".format(self)


class JobLog(ResultModelBase):
    """JobLog result."""

    __tablename__ = "logs"
    __table_args__ = {"sqlite_autoincrement": True}

    id = sa.Column(
        sa.Integer,
        sa.Sequence("logs_id_sequence"),
        autoincrement=True,
        primary_key=True,
    )

    task_id = sa.Column(sa.String(155), nullable=False, index=True)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    message = sa.Column(sa.UnicodeText(), nullable=False, default="")
    configuration = sa.Column(sa.UnicodeText(), nullable=False, default="")
    parent_tasklet = sa.Column(sa.UnicodeText(), nullable=False, default="")
    parent_task_id = sa.Column(sa.UnicodeText(), nullable=False, default="")
    current_task = sa.Column(sa.UnicodeText(), nullable=False, default="")
    current_tasklet = sa.Column(sa.UnicodeText(), nullable=False, default="")
    current_task_id = sa.Column(sa.String(255), nullable=False, default="")
    level = sa.Column(sa.String(64), nullable=False, default="")
    stdout = sa.Column(sa.UnicodeText(), nullable=False, default="")
    exc_info = sa.Column(sa.UnicodeText(), nullable=False, default="")
    created_by_user_id = sa.Column(sa.Integer, nullable=False)

    def __repr__(self):
        return "<job {0}>".format(self.id)
