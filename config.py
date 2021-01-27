# api/config.py

import os
from dotenv import load_dotenv, find_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# print("FLASK_ENV==============>", os.getenv("FLASK_ENV", None))
# print("LOCAL_DOCKER==============>", os.getenv("LOCAL_DOCKER", None))

if os.getenv("FLASK_ENV", None) == "production":
    filename = ".env"
elif os.getenv("FLASK_ENV", None) == "development" and os.getenv("LOCAL_DOCKER", None):
    filename = ".env.development"
else:
    filename = ".env.development.local"

# print("EnvFilename==============>", filename)

load_dotenv(
    find_dotenv(filename=filename, raise_error_if_not_found=True),
    override=True,
)

# print(
#     "REDIS_CONNECTION_URL==============>",
#     os.getenv("REDIS_URL", "redis://redis:6379/0"),
# )


class BaseConfig(object):
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "pretty-strong-secret")
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///temp.db")
    # SQLALCHEMY_ENGINE_OPTIONS = {'pool_size' : 100, 'pool_recycle' : 3600, 'pool_pre_ping': True}
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SOCKETIO_MESSAGE_QUEUE = os.getenv("SOCKETIO_MESSAGE_QUEUE", REDIS_URL)
    QUEUES = ["default", "low", "medium", "high"]
    SOCKETIO_ENABLED = (
        True if os.getenv("SOCKETIO_ENABLED", "False") == "True" else False
    )

    """Logger"""
    LOG_TO_STDOUT = False
    PROD_LOG_MAIL = False

    """Mail Config For Email Handler"""
    # MAIL_PORT = int(os.getenv('MAIL_PORT') or 587)
    # MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', False)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT") or 465)
    MAIL_USE_SSL = int(os.getenv("MAIL_USE_TLS", True))  # 1=True, 0=False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "test@gmail.com")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER_NAME", "Cool App Platform"),
        os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME),
    )
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "CoreaiID977{")
    MAIL_ADMIN = os.getenv("MAIL_ADMIN", "test@gmail.com")

    """File Uploads Config"""
    IMAGE_UPLOADS = f"{basedir}/project/static/logos/"
    CLIENT_CSV_UPLOADS = f"{basedir}/project/static/client_csv/"
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
    ALLOWED_FILE_EXTENSIONS = ["PDF", "DOCX", "DOC", "TXT", "CSV"]


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    LOG_TO_STDOUT = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_DEV_URL")


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    LOG_TO_STDOUT = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_TEST_URL")
    SOCKETIO_MESSAGE_QUEUE = None
    MAIL_SUPPRESS_SEND = False


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    PROD_LOG_MAIL = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


"""
Exposing Configs in dict
"""
configs = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": BaseConfig,
}

"""
Setting for Alembic (Leagcy)
"""
alembicArgs = [
    "--raiseerr",
    "upgrade",
    "head",
]

"""
CORS headers settings
"""
allowed_origins = "*"
cors_headers = [
    "Access-Control-Allow-Credentials",
    "Access-Control-Allow-Origin",
    "Content-Type",
    "Accept",
]

"""
Default Error Handler Settings
"""
error_handler_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s: %(message)s "
            "[in %(pathname)s:%(lineno)d]",
        }
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default",
        }
    },
    "root": {"level": "ERROR", "handlers": ["wsgi"]},
}


"""
Error Levels
"""
error_levels = {
    50: "CRITICAL",
    40: "ERROR",
    30: "WARNING",
    20: "INFO",
    10: "DEBUG",
    0: "NOTSET",
}

"""
For both, common and specific templates
- html_data, email_template, email_subject & recipients are mandatory keywords
- keys inside html_data depends upon your requirement for html contents
"""
deafult_email_template_contents = {
    "html_data": {
        "action_url": "http://",
        "title": "Verify your email address",
        "content_heading": "Verify your email address",
        "main_content": "Thanks for signing up! We're excited to have you as an early user.",
        "button_text": "Verify Email",
    },
    "email_template": "<EmailTemplate.WELCOME_ABOARD>",
    "email_subject": "<EmailTemplate.WELCOME_ABOARD_SUBJECT>",
    "recipients": ["<user_email>"],
}

"""
QR code image base url for 2FA-OTP
"""
qr_code_image_base_url = "https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl="

"""
Default User Security questions. 

- Future enhancement:
    - if questions get changed, we need to update (re-write) logics when answers are saved in db.
"""
user_security_questions = {
    "question_one": "What was your childhood nickname?",
    "question_two": "What is the name of your favourite city?",
    "question_three": "What was your dream job as a child?",
}
