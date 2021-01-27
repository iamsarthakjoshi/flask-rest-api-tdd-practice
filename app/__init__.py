import os, logging
import stripe
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from redis import Redis
from rq import Queue

# import alembic.config # Legacy alembic DB service
# from app.database import MySQLService # Legacy MySQL DB service
from app.config import ConfigSetup
from app.logger import CustomLogger
from config import alembicArgs, allowed_origins, cors_headers

# flask extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
mail = Mail()
stripe.api_key = os.getenv("STRIPE_API_KEY")

# import models to let Flask_Sqlalchemy & flask_migrate know
from app.models import (
    User,
    Task,
)

# custom extension
config_setup = ConfigSetup()
custom_logger = CustomLogger()


def create_app(main=True):
    # initialise Flask
    app = Flask(
        __name__, template_folder="client/templates", static_folder="client/static"
    )

    # config setup
    config_setup.init_app(app)

    # Legacy - alembic DB service
    # alembic.config.main(argv=alembicArgs)
    # MySQLService.init_db(app)

    # initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # initialize redis and rq
    low_queue = app.config["QUEUES"][1]
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.rq = Queue(connection=app.redis, name=low_queue)

    # control socketio
    is_socketio_enabled = app.config["SOCKETIO_ENABLED"]
    socketio_msg_queue = app.config["SOCKETIO_MESSAGE_QUEUE"]
    if main:
        socketio.init_app(
            app,
            cors_allowed_origins="*",
            message_queue=socketio_msg_queue,
        )
    else:
        socketio.init_app(
            None,
            cors_allowed_origins="*",
            async_mode="threading",
            message_queue=socketio_msg_queue,
        )

    CORS(app, origins=allowed_origins, supports_credentials=True, headers=cors_headers)

    with app.app_context():
        # initialize custom logger
        custom_logger.init_app(
            level=logging.CRITICAL, mail=False if app.debug else True
        )

        # add blueprints
        from app.routes import api_bp

        app.register_blueprint(blueprint=api_bp, url_prefix="/api")

        # shell context for flask cli
        app.shell_context_processor({"app": app, "db": db})

    return app
