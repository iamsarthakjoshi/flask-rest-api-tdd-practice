import os
import sys
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import current_app as app
from flask.logging import default_handler
from config import error_handler_config


class CustomLogger:
    def __init__(self):
        self.handler = None
        self.level = logging.INFO

    def init_app(self, default=False, level=None, mail=False, **kwargs):
        if not level:
            level = self.level

        if mail:
            self.handler = self.mail_error_handler_logger()
            self.set_handler(level)
            return

        if default:
            self.default_stdout_logger()
        elif not app.debug and not app.testing and app.config["PROD_LOG_MAIL"]:
            self.handler = self.mail_error_handler_logger()
        else:
            if app.config["LOG_TO_STDOUT"]:
                self.handler = self.stdout_handler_logger()
            else:
                self.handler = self.rotating_file_logger()

        # assign handler and log level
        self.set_handler(level)

    def set_handler(self, level):
        if self.handler:
            self.handler.setLevel(level)
            app.logger.addHandler(self.handler)
        else:
            self.default_stdout_logger()

    def mail_error_handler_logger(self):
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
                secure = None
                if app.config["MAIL_USE_SSL"]:
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost=(app.config["MAIL_SERVER"], 587),
                    fromaddr=app.config["MAIL_USERNAME"],
                    toaddrs=[app.config["MAIL_ADMIN"]],
                    subject="CoolApp - Backend Service Logs For Service-Startup, Warning, Error and Critical levels.",
                    credentials=auth,
                    secure=secure,
                )
                return mail_handler

    def stdout_handler_logger(self):
        stream_handler = logging.StreamHandler(sys.stdout)  # default is sys.stderr
        stream_handler.setFormatter(
            logging.Formatter(
                fmt="[%(asctime)s] %(levelname)s: %(message)s "
                "[in %(pathname)s:%(lineno)d]"
            )
        )
        return stream_handler

    def rotating_file_logger(self):
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/app.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s: %(message)s "
                "[in %(pathname)s:%(lineno)d]"
            )
        )
        return file_handler

    def default_stdout_logger(self):
        app.logger.removeHandler(default_handler)
        app.logger.handlers.clear()  # prevent duplicate debug messages
        from logging.config import dictConfig

        dictConfig(error_handler_config)


# this article could be helpful if you need to implement multiple logger handlers.
# https://stackoverflow.com/questions/46453726/how-to-manage-multiple-loggers-in-python-flask-tornado-application
