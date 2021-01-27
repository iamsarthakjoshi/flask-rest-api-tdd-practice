import gevent
from rq import get_current_job
from flask import render_template, current_app as app
from flask_mail import Message
from uuid import uuid4

from app import db, create_app, mail
from app.models import Task
from app.events import push_data
from app.util import format_error_log
from app.constants import TaskType, EmailTemplate

# main_app = create_app()
aux_app = create_app(main=False)


def test_task(**kwargs):
    with aux_app.app_context():
        job_id = str(get_current_job().get_id())
        print(f"Starting long task {job_id}")
        # register this task
        task = Task.query.get(job_id)
        task.completed = True
        db.session.commit()
        print("Ended long task", str(task.completed))
    app.logger.info(f"Ended long task {str(task.completed)}")
    return "Some Data From Long Task"


def send_email_with_template(task_type=None, **kwargs):
    """
    Args:
        kwargs: refer to "deafult_email_template_contents" in config.py file
    """
    user_id = kwargs["user_id"] if "user_id" in kwargs else None
    subject = kwargs["email_subject"]
    with aux_app.app_context():
        try:
            job_id = get_current_job().get_id()
            # udpate this task info
            task = Task.query.get(job_id)
            task.description = f"Sending {subject} email."
            task.user_id = user_id
            db.session.commit()

            # send the message
            recipients = kwargs["recipients"]
            html_data = kwargs["html_data"]
            msg = Message(subject=subject, recipients=recipients)
            msg.html = render_template(
                template_name_or_list=kwargs["email_template"],
                data=html_data,
            )
            mail.send(msg)
            # send_email(
            #     subject=subject,
            #     recipients=recipients,
            #     template=kwargs['email_template'],
            #     html_data=html_data
            # )

            # email sent at this point, so set task completed
            task.completed = True
            app.logger.info(
                f"Task send_email_with_template completed. Task/Job Id: {job_id}"
            )
        except Exception as e:
            # set task incomplete
            task.completed = False
            app.logger.error(
                format_error_log(
                    at="send_email_with_template", message=f"Task/Job Id: {job_id}"
                )
            )

            # send emails faliure message if needed
        finally:
            # commit db transactions
            db.session.commit()

    # def send_email(subject, recipients, template, html_data):
    #     # send the message
    #     msg = Message(subject, recipients)
    #     msg.html = render_template(template, html_data)
    #     mail.send(msg)


# TODO: Not working atm. Need to Fix it. Issue: Task is not returned.
# def register_task(user_id, description):
#     """
#         This function must be called inside aux_app context to get access to db, mail and other extensions.

#         Arguments:
#             - user_id: string
#             - description: string
#         Returns:
#             - Task Model Object
#     """
#     try:
#         rq_job_id = get_current_job().get_id()
#         task = Task.query.get(rq_job_id)
#         # udpate this task info
#         task.description = f"Sending {subject} email to user id {user_id}."
#         task.user_id = user_id
#         db.session.commit()
#         return Task.query.get(rq_job_id)
#     except Exception as e:
#         app.logger.error(format_error_log(at="register_task"))
#         return None
