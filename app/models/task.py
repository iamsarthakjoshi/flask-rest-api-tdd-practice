from flask import current_app
from rq.job import Job
from rq.exceptions import NoSuchJobError
from redis.exceptions import RedisError
from rq.registry import (
    FailedJobRegistry,
    StartedJobRegistry,
    FinishedJobRegistry,
    DeferredJobRegistry,
    ScheduledJobRegistry,
)
from app import db


class Task(db.Model):
    id = db.Column(db.String(128), primary_key=True, unique=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128), nullable=True)
    user_id = db.Column(db.String(77), nullable=True)
    completed = db.Column(db.Boolean)

    def __repr__(self):
        return f"Task Id: {self.id} Name: {self.name} Done:{self.completed}"

    def __init__(self, id, name, description=None, user_id=None, completed=None):
        self.id = id
        self.name = name
        self.description = description
        self.user_id = user_id
        self.completed = completed

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "completed": self.completed,
        }

    @staticmethod
    def get_tasks():
        return [t.to_dict() for t in Task.query.all()]

    @staticmethod
    def get_task(id):
        return Task.query.get(id).to_dict()

    @staticmethod
    def get_tasks_by_user_id(user_id):
        return [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]

    @staticmethod
    def get_rq_job(job_id=None):
        try:
            if job_id:
                rq_job = Job.fetch(job_id, connection=current_app.redis)
            else:
                return None
        except (RedisError, NoSuchJobError):
            return None
        return rq_job

    @staticmethod
    def get_rq_jobs():
        started_job_registry = StartedJobRegistry(queue=current_app.rq)
        finished_job_registry = FinishedJobRegistry(queue=current_app.rq)
        failed_job_registry = FailedJobRegistry(queue=current_app.rq)
        deferred_job_registry = DeferredJobRegistry(queue=current_app.rq)
        scheduled_job_registry = ScheduledJobRegistry(queue=current_app.rq)
        task = dict()

        task["started"] = list()
        for statrted_job_job_id in started_job_registry.get_job_ids():
            job = Job.fetch(statrted_job_job_id, connection=current_app.redis)
            task["started"].append({"job_id": job.id, "job_info": job.exc_info})

        task["finished"] = list()
        for finished_job_job_id in finished_job_registry.get_job_ids():
            job = Job.fetch(finished_job_job_id, connection=current_app.redis)
            task["finished"].append({"job_id": job.id, "job_info": job.exc_info})

        task["failed"] = list()
        for failed_job_id in failed_job_registry.get_job_ids():
            job = Job.fetch(failed_job_id, connection=current_app.redis)
            task["failed"].append({"job_id": job.id, "job_info": job.exc_info})

        task["deferred"] = list()
        for deferred_job_job_id in deferred_job_registry.get_job_ids():
            job = Job.fetch(deferred_job_job_id, connection=current_app.redis)
            task["deferred"].append({"job_id": job.id, "job_info": job.exc_info})

        task["scheduled"] = list()
        for scheduled_job_job_id in scheduled_job_registry.get_job_ids():
            job = Job.fetch(scheduled_job_job_id, connection=current_app.redis)
            task["scheduled"].append({"job_id": job.id, "job_info": job.exc_info})
        return task

    @staticmethod
    def remove_failed_rq_jobs_from_registery(delete_job=False):
        registry = FailedJobRegistry(queue=current_app.rq)
        for job_id in registry.get_job_ids():
            registry.remove(job_id, delete_job=delete_job)

    @staticmethod
    def remove_failed_rq_job_from_registery(job_id, delete_job=False):
        if job_id:
            registry = FailedJobRegistry(queue=current_app.rq)
            for _job_id in registry.get_job_ids():
                if _job_id == job_id:
                    registry.remove(job_id, delete_job=delete_job)
