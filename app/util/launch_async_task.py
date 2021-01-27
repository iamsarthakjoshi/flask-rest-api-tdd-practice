from flask import current_app as app

from app import db
from app.models import Task

logger = app.logger


def launch_async_task(name, description=None, task_type=None, *args, **kwargs):
    if not app.testing:
        with app.app_context():
            rq_job = app.rq.enqueue("app.tasks." + name, task_type=task_type, **kwargs)
            job_id = rq_job.get_id()
            task = Task(id=job_id, name=name)
            db.session.add(task)
            db.session.commit()
            logger.info(f"Task {name} has been launched. RqJobId: {job_id}")
            return job_id
